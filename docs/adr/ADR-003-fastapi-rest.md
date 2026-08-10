# ADR-003 : FastAPI REST pour le Backend

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect nécessite un **backend robuste, performant et maintenable** pour gérer :

1. **L'authentification** des parents et des élèves
2. **La gestion des données** (compétences, évaluations, contenus)
3. **Les requêtes RESTful** depuis le frontend Next.js
4. **Les tâches asynchrones** (processing H5P, etc.)
5. **La validation des données** avec typage fort

### Problème à résoudre

Choisir le **framework backend** et l'**architecture API** qui répondent aux exigences suivantes :

- **Performance** : Réponse rapide aux requêtes
- **Typage** : Code type-safe avec validation
- **Maintenabilité** : Structure claire et extensible
- **Documentation** : API auto-documentée
- **Compatibilité** : Intégration facile avec Next.js frontend
- **Écosystème** : Bibliothèques Python matures

### Contraintes

- Équipe familière avec Python
- Besoin de **validation stricte** des entrées
- **Async support** pour les opérations bloquantes
- **Documentation automatique** de l'API
- **Pas de GraphQL** (décision dans DECISIONS_FINALES.md)

---

## Décision

**Adopter FastAPI** comme framework backend avec une **architecture REST**.

### Stack Backend Complète

```
Backend Stack:
├── Framework: FastAPI
├── Language: Python 3.11+
├── Async: ASGI (Uvicorn/Hypercorn)
├── ORM: SQLAlchemy 2
├── Migrations: Alembic
├── Validation: Pydantic
├── Database: PostgreSQL
├── Cache: Redis
├── Task Queue: Celery
├── Testing: Pytest
└── Documentation: OpenAPI/Swagger
```

---

## Options considérées

### 1. FastAPI + REST

**Pour** :
- ✅ **Performance excellente** : Un des frameworks Python les plus rapides
- ✅ **Typage natif** : Intégration parfaite avec Pydantic et type hints
- ✅ **Documentation automatique** : OpenAPI/Swagger générée automatiquement
- ✅ **Async natif** : Support ASGI pour les opérations asynchrones
- ✅ **Validation intégrée** : Request/response validation avec Pydantic
- ✅ **Dependency Injection** : Système de dépendances puissant
- ✅ **Écosystème moderne** : Compatible avec les dernières versions de Python
- ✅ **Facile à apprendre** : Syntaxe intuitive et claire
- ✅ **Tests faciles** : Intégration simple avec pytest

**Contre** :
- ❌ Framework relativement jeune (mais stable)
- ❌ Moins de "batteries included" que Django

**Verdict** : ✅ **Sélectionné** - Meilleur choix pour nos besoins modernes

---

### 2. Django REST Framework

**Pour** :
- ✅ Framework mature et éprouvé
- ✅ "Batteries included" (admin, auth, ORM)
- ✅ Grande communauté et documentation
- ✅ Bonnes performances

**Contre** :
- ❌ **Interdit** par DECISIONS_FINALES.md (Choix exclus)
- ❌ Plus lourd que FastAPI
- ❌ Moins moderne (WSGI vs ASGI)
- ❌ Configuration plus complexe
- ❌ Moins flexible pour les APIs modernes

**Verdict** : ❌ **Rejeté** - Explicitement interdit

---

### 3. Flask + Extensions

**Pour** :
- ✅ Léger et flexible
- ✅ Micro-framework, contrôle total
- ✅ Bon écosystème d'extensions

**Contre** :
- ❌ Pas de typage natif (à ajouter manuellement)
- ❌ Pas de validation intégrée
- ❌ Documentation manuelle de l'API
- ❌ Async moins mature
- ❌ Plus de code boilerplate

**Verdict** : ❌ **Rejeté** - FastAPI offre tout cela nativement

---

### 4. FastAPI + GraphQL (Strawberry/Ariadne)

**Pour** :
- ✅ Typage fort
- ✅ Flexibilité des requêtes

**Contre** :
- ❌ **Interdit** par DECISIONS_FINALES.md (Choix exclus : pas GraphQL)
- ❌ Plus complexe à mettre en place
- ❌ Surkill pour nos besoins
- ❌ Moins performant que REST pour nos cas d'usage

**Verdict** : ❌ **Rejeté** - Explicitement interdit + REST est suffisant

---

### 5. Starlette (sans FastAPI)

**Pour** :
- ✅ Très léger
- ✅ ASGI natif
- ✅ Base de FastAPI

**Contre** :
- ❌ Pas de validation intégrée
- ❌ Pas de documentation automatique
- ❌ Plus de code à écrire

**Verdict** : ❌ **Rejeté** - FastAPI apporte trop de valeur ajoutée

---

## Conséquences

### Conséquences positives

- **Développement rapide** : Moins de code boilerplate
- **Code maintenable** : Typage fort + validation intégrée
- **Documentation automatique** : Swagger UI et ReDoc générés
- **Performance excellente** : Un des frameworks Python les plus rapides
- **Async support** : Gestion des opérations bloquantes sans bloquer
- **Intégration facile** : Travaille parfaitement avec Next.js frontend
- **Tests simplifiés** : Client de test intégré

### Conséquences négatives

- **Moins de "batteries included"** que Django (admin, auth)
- **Écosystème plus jeune** (mais en croissance rapide)

### Mitigations

- **Ajouter les fonctionnalités manquantes** via des bibliothèques tierces
- **Utiliser des packages matures** pour l'auth, admin, etc.
- **Contribuer à l'écosystème** en publiant nos solutions

---

## Validation

### Compatibilité avec les exigences

| Exigence | FastAPI + REST | Score |
|----------|----------------|-------|
| Performance | ✅ Excellente | 10/10 |
| Typage | ✅ Natif (Pydantic) | 10/10 |
| Validation | ✅ Intégrée | 10/10 |
| Documentation | ✅ Auto-générée | 10/10 |
| Async | ✅ Natif (ASGI) | 10/10 |
| Intégration Frontend | ✅ Excellente | 10/10 |
| Maintenabilité | ✅ Excellente | 9/10 |
| Écosystème | ✅ Bon | 8/10 |

### Benchmark de performance

Selon [TechEmpower Web Framework Benchmarks](https://www.techempower.com/benchmarks/) :
- FastAPI se classe parmi les frameworks Python les plus performants
- Se compare favorablement avec Node.js/Express et Go

---

## Implémentation

### Structure du projet api/

```
apps/api/
├── main.py                  # Point d'entrée FastAPI
├── config.py                # Configuration
├── dependencies.py          # Dépendances (DI)
├── exceptions.py            # Gestion des erreurs
├── models/
│   ├── __init__.py
│   ├── base.py             # Base model
│   ├── user.py            # Modèle User
│   └── ...               # Autres modèles
├── routes/
│   ├── __init__.py
│   ├── api.py             # Router principal
│   ├── auth.py            # Routes d'auth
│   ├── users.py           # Routes users
│   └── ...               # Autres routes
├── schemas/
│   ├── __init__.py
│   ├── user.py            # Schémas Pydantic
│   └── ...               # Autres schémas
├── services/
│   ├── __init__.py
│   ├── auth.py            # Service d'auth
│   └── ...               # Autres services
├── utils/
│   ├── __init__.py
│   ├── security.py        # Utilitaires de sécurité
│   └── ...               # Autres utilitaires
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Fixtures
│   └── test_*.py          # Tests
├── alembic/
│   └── versions/          # Migrations
├── requirements.txt
├── pyproject.toml
└── Dockerfile
```

### Configuration de base

1. **main.py** :
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="StudentConnect API",
    description="API REST pour StudentConnect",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from routes import api
app.include_router(api.router)
```

2. **requirements.txt** :
```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic==2.6.0
pydantic-settings==2.2.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
celery==5.3.6
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Framework trop jeune | Faible | Moyen | FastAPI est déjà très mature |
| Écosystème limité | Faible | Moyen | L'écosystème grandit rapidement |
| Performances insuffisantes | Très faible | Élevé | Benchmark avant déploiement |
| Complexité async | Moyenne | Moyen | Formation sur ASGI/Python async |

---

## Références

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Performance](https://fastapi.tiangolo.com/#performance)
- [ASGI vs WSGI](https://fastapi.tiangolo.com/async/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/14/orm/)
- [TechEmpower Benchmarks](https://www.techempower.com/benchmarks/)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Comparaison des frameworks Python

| Critère | FastAPI | Django RF | Flask | Starlette |
|---------|---------|-----------|-------|-----------|
| Performance | ✅ 10/10 | ⚠️ 7/10 | ⚠️ 7/10 | ✅ 9/10 |
| Typage | ✅ 10/10 | ⚠️ 6/10 | ❌ 4/10 | ⚠️ 7/10 |
| Validation | ✅ 10/10 | ⚠️ 7/10 | ❌ 4/10 | ❌ 4/10 |
| Documentation | ✅ 10/10 | ✅ 9/10 | ❌ 5/10 | ❌ 5/10 |
| Async | ✅ 10/10 | ❌ 4/10 | ⚠️ 6/10 | ✅ 9/10 |
| Écosystème | ✅ 8/10 | ✅ 10/10 | ✅ 8/10 | ⚠️ 6/10 |
| Simplicité | ✅ 9/10 | ⚠️ 7/10 | ✅ 8/10 | ✅ 9/10 |

### Bonnes pratiques FastAPI

1. **Séparer les concerns** : Routes, services, modèles
2. **Utiliser les dépendances** pour l'injection (DI)
3. **Valider toutes les entrées** avec Pydantic
4. **Documenter avec des exemples** dans les schémas
5. **Gérer les erreurs proprement** avec HTTPException
6. **Utiliser les background tasks** pour les opérations longues
7. **Sécuriser l'API** avec JWT ou sessions
8. **Optimiser les performances** avec le caching

### Architecture Modular Monolith

Le backend sera structuré comme un **modular monolith** :
- Un seul déploiement (conteneur Docker)
- Modules clairs et séparés (auth, users, contents, etc.)
- Communication interne via appels de fonctions
- Possibilité de split en microservices plus tard si nécessaire
