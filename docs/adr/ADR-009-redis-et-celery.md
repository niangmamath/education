# ADR-009 : Redis et Celery pour les Tâches Asynchrones

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit gérer des **opérations longues et asynchrones** :
- Processing des uploads H5P (extraction, validation)
- Génération de rapports et analyses
- Envoi d'emails (vérification, notifications)
- Nettoyage et maintenance

### Problème à résoudre

Choisir une solution pour les **tâches asynchrones** qui offre :
- **Fiabilité** : Les tâches ne sont pas perdues
- **Scalabilité** : Peut gérer une charge croissante
- **Simplicité** : Facile à configurer et maintenir
- **Compatibilité** : Travaille avec FastAPI/Python
- **Monitoring** : Visibilité sur l'état des tâches

### Contraintes

- **Redis** pour le broker (décision dans DECISIONS_FINALES.md)
- **Celery** pour les workers (décision dans DECISIONS_FINALES.md)
- Intégration avec FastAPI
- Docker compatible

---

## Décision

**Utiliser Celery avec Redis comme broker** pour la gestion des tâches asynchrones.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI (Backend)                           │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  API Endpoints:                                             │  │
│  │  - POST /tasks/upload-h5p (démarre une tâche Celery)      │  │
│  │  - GET /tasks/{id} (vérifie l'état)                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │ Publique tâche dans queue Redis
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Redis (Broker)                              │
│  - Queue: celery (tâches à exécuter)                          │
│  - Queue: high_priority (tâches urgentes)                    │
│  - Storage: résultats des tâches                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Celery Workers                             │
│  ┌─────────────────────┐ ┌─────────────────────┐              │
│  │  Worker 1           │ │  Worker 2           │              │
│  │  - Consomme de Redis│ │  - Consomme de Redis│              │
│  │  - Exécute les tâches│ │  - Exécute les tâches│              │
│  │  - Stocke résultats │ │  - Stocke résultats │              │
│  └─────────────────────┘ └─────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## Options considérées

### 1. Celery + Redis (Sélectionné)

**Pour** :
- ✅ **Mature et éprouvé** : Utilisé dans de nombreux projets
- ✅ **Redis comme broker** : Rapide et simple
- ✅ **Résultats stockés** dans Redis
- ✅ **Scalable** : Ajout de workers facile
- ✅ **Retries automatiques** : Gestion des échecs
- ✅ **Scheduling** : Tâches périodiques (Celery Beat)
- ✅ **Monitoring** : Flower pour le monitoring
- ✅ **Docker friendly** : Conteneurs séparés

**Contre** :
- ❌ Configuration initiale complexe
- ❌ Nécessite plusieurs services (Redis, Workers)

**Verdict** : ✅ **Sélectionné**

---

### 2. RQ (Redis Queue)

**Pour** :
- ✅ Plus simple que Celery
- ✅ Redis natif

**Contre** :
- ❌ Moins de features (retries, scheduling, etc.)
- ❌ Moins mature
- ❌ Moins de documentation

**Verdict** : ❌ **Rejeté** - Celery offre plus de fonctionnalités

---

### 3. ARQ (Async Redis Queue)

**Pour** :
- ✅ Async natif
- ✅ Performant

**Contre** :
- ❌ Moins mature
- ❌ Moins de community support

**Verdict** : ❌ **Rejeté** - Moins stable

---

### 4. Huey

**Pour** :
- ✅ Simple
- ✅ Supports Redis

**Contre** :
- ❌ Moins de features
- ❌ Moins actif

**Verdict** : ❌ **Rejeté** - Celery est plus complet

---

## Conséquences

### Avantages

- **Découplage** : Le frontend n'attend pas les tâches longues
- **Résilience** : Les tâches sont réessayées en cas d'échec
- **Scalabilité** : Ajout de workers selon la charge
- **Flexibilité** : Peut exécuter n'importe quelle tâche Python
- **Monitoring** : Visibilité complète avec Flower

### Inconvénients

- **Complexité** : Plusieurs services à gérer
- **Debugging** : Plus complexe que du code synchrone
- **Ressources** : Nécessite des workers dédiés

### Mitigations

- **Docker Compose** : Configuration simplifiée
- **Logging structuré** : Pour faciliter le debugging
- **Health checks** : Monitoring des workers
- **Limites** : Configurer des timeouts raisonnables

---

## Implémentation

### Configuration Celery

```python
# celery_app.py
from celery import Celery
from celery.schedules import crontab

app = Celery(
    'studentconnect_tasks',
    broker='redis://redis:6379/1',
    backend='redis://redis:6379/2',
    include=['tasks.h5p_tasks', 'tasks.email_tasks']
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,  # 1 heure
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    retry_policy={
        'timeout': 30,
        'max_retries': 3,
        'delay': 60
    }
)

# Tâches périodiques (Celery Beat)
app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'tasks.cleanup.cleanup_temp_files',
        'schedule': crontab(hour=2, minute=0),  # 2h du matin
    },
    'send-daily-reports': {
        'task': 'tasks.reports.send_daily_reports',
        'schedule': crontab(hour=8, minute=0),  # 8h du matin
    },
}
```

### Tâches exemple

```python
# tasks/h5p_tasks.py
from celery_app import app
from services.h5p_service import H5PService
import logging

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)
def process_h5p_upload(self, upload_id: str, user_id: str):
    """Traite un upload H5P : extraction, validation, stockage"""
    try:
        h5p_service = H5PService()
        result = h5p_service.process_upload(upload_id, user_id)
        return result
    except Exception as e:
        logger.error(f"Erreur traitant H5P upload {upload_id}: {e}")
        self.retry(exc=e, countdown=60)

@app.task()
def generate_thumbnail(h5p_package_id: str, version: str):
    """Génère une miniature pour un paquet H5P"""
    # Implémentation...
    pass
```

### Docker Compose

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  celery-worker:
    build: .
    command: celery -A celery_app worker -l info
    depends_on:
      redis:
        condition: service_healthy
      api:
        condition: service_started
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - .:/app

  celery-beat:
    build: .
    command: celery -A celery_app beat -l info
    depends_on:
      redis:
        condition: service_healthy
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
    volumes:
      - .:/app

  flower:
    build: .
    command: celery -A celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      redis:
        condition: service_healthy
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1

volumes:
  redis_data:
```

### Intégration FastAPI

```python
# routes/tasks.py
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from celery_app import app as celery_app
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: dict = None
    error: str = None

@router.post("/upload-h5p")
async def upload_h5p(upload_data: dict):
    """Démarre une tâche de processing H5P"""
    task = process_h5p_upload.delay(upload_data["upload_id"], upload_data["user_id"])
    return {"task_id": task.id}

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Vérifie l'état d'une tâche"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
        "error": str(task_result.result) if task_result.failed() else None
    }
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Tâches bloquées | Faible | Élevé | Timeouts, monitoring |
| Redis downtime | Faible | Élevé | Cluster Redis, fallback |
| Perte de tâches | Très faible | Élevé | ACK après exécution, retries |
| Worker crash | Moyenne | Moyen | Auto-restart, health checks |
| Deadlock | Faible | Moyen | Design soigneux des tâches |

---

## Références

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)
- [Flower (Monitoring)](https://flower.readthedocs.io/)
- [Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
