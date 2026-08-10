# ADR-004 : PostgreSQL et SQLAlchemy 2 pour la Persistance

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit stocker des données **relationnelles et structurées** :
- Utilisateurs (parents, élèves)
- Compétences et arbre de prérequis
- Résultats d'évaluation
- Lacunes détectées
- Contenus H5P et métadonnées
- Sessions et historique

### Problème à résoudre

Choisir le **SGBD** et l'**ORM** qui offrent :
- **Fiabilité** et intégrité des données
- **Performance** pour les requêtes complexes
- **Flexibilité** pour les relations
- **Maintenabilité** du schéma
- **Compatibilité** avec FastAPI et Python async

### Contraintes

- Données **relationnelles** avec relations complexes (arbre de compétences)
- Besoin de **transactions ACID**
- **Requêtes complexes** (jointures, agrégations)
- **Migration** du schéma au fil du temps
- **Interdit** : Neo4j (décision dans DECISIONS_FINALES.md)

---

## Décision

**Adopter PostgreSQL** comme SGBD avec **SQLAlchemy 2** comme ORM et **Alembic** pour les migrations.

### Stack Persistance Complète

```
Persistence Stack:
├── Database: PostgreSQL 15+
├── ORM: SQLAlchemy 2.0
├── Migrations: Alembic
├── Connection Pool: SQLAlchemy async
├── Async Driver: asyncpg
└── Admin: pgAdmin ou équivalent
```

---

## Options considérées

### 1. PostgreSQL + SQLAlchemy 2 + Alembic

**Pour** :
- ✅ **SGBD mature** : PostgreSQL est l'un des SGBD open source les plus fiables
- ✅ **Support JSON** : Permet de stocker des données semi-structurées
- ✅ **Requêtes avancées** : Full-text search, CTEs, window functions
- ✅ **SQLAlchemy 2 moderne** : Meilleure performance, typage amélioré
- ✅ **Alembic** : Migrations robustes et versionnées
- ✅ **Async support** : asyncpg pour les requêtes asynchrones
- ✅ **Extensions** : PostgreSQL a un écosystème riche d'extensions
- ✅ **Communauté** : Grande communauté et documentation

**Contre** :
- ❌ Configuration légèrement plus complexe que SQLite
- ❌ Nécessite un serveur séparé (vs SQLite embarqué)

**Verdict** : ✅ **Sélectionné** - Meilleur choix pour nos besoins

---

### 2. MySQL + SQLAlchemy

**Pour** :
- ✅ SGBD mature et populaire
- ✅ Bonne performance
- ✅ Large écosystème

**Contre** :
- ❌ Moins de features avancées que PostgreSQL
- ❌ Moins bon support JSON
- ❌ Licence moins permissive (pour certaines versions)

**Verdict** : ❌ **Rejeté** - PostgreSQL offre plus de features

---

### 3. SQLite + SQLAlchemy

**Pour** :
- ✅ Simple à configurer
- ✅ Embarqué, pas de serveur
- ✅ Parfait pour développement/local

**Contre** :
- ❌ Pas adapté pour production avec charge élevée
- ❌ Pas de concurrency élevée
- ❌ Limitations pour les requêtes complexes
- ❌ Pas de contrôle d'accès fin

**Verdict** : ❌ **Rejeté** - Pas adapté pour un MVP en production

---

### 4. MongoDB + Beanie/Motor

**Pour** :
- ✅ Flexibilité du schéma
- ✅ Facile à scaler horizontalement
- ✅ Bon pour les données non structurées

**Contre** :
- ❌ **Interdit** : Neo4j est interdit, mais MongoDB aussi par inférence (pas relationnel)
- ❌ Pas de transactions ACID complètes
- ❌ Moins adapté pour les relations complexes (arbre de compétences)
- ❌ Pas de joins natifs
- ❌ Moins bon pour les requêtes d'agrégation complexes

**Verdict** : ❌ **Rejeté** - Pas adapté pour des données relationnelles

---

### 5. Neo4j

**Pour** :
- ✅ Optimisé pour les graphes
- ✅ Bon pour les relations complexes

**Contre** :
- ❌ **Explicitement interdit** par DECISIONS_FINALES.md
- ❌ Pas adapté pour les données tabulaires
- ❌ Moins mature pour les applications web classiques

**Verdict** : ❌ **Rejeté** - Explicitement interdit

---

## Conséquences

### Conséquences positives

- **Fiabilité** : PostgreSQL est connu pour sa stabilité
- **Performance** : Optimisé pour les requêtes complexes
- **Flexibilité** : SQLAlchemy permet d'écrire du SQL brut quand nécessaire
- **Maintenabilité** : Alembic gère les migrations proprement
- **Extensibilité** : Facile d'ajouter des tables et relations
- **Async** : Support complet pour async/await

### Conséquences négatives

- **Complexité** : Configuration légèrement plus complexe
- **Learning curve** : SQLAlchemy 2 a des différences avec v1.x
- **Dépendance externe** : Nécessite un serveur PostgreSQL

### Mitigations

- **Docker** : Conteneuriser PostgreSQL pour un déploiement simple
- **Scripts** : Créer des scripts pour les opérations courantes
- **Documentation** : Bien documenter la configuration
- **Tests** : Tester les migrations automatiquement dans CI

---

## Validation

### Compatibilité avec les exigences

| Exigence | PostgreSQL + SQLAlchemy 2 | Score |
|----------|----------------------------|-------|
| Fiabilité | ✅ Excellente | 10/10 |
| Performance | ✅ Excellente | 10/10 |
| Relations complexes | ✅ Excellente | 10/10 |
| Transactions | ✅ Complètes | 10/10 |
| Async support | ✅ Natif (asyncpg) | 10/10 |
| Migrations | ✅ Robustes (Alembic) | 10/10 |
| Écosystème | ✅ Riche | 9/10 |

### Schéma exemple

```sql
-- Table des parents
CREATE TABLE auth_parents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des enfants
CREATE TABLE auth_children (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES auth_parents(id) ON DELETE CASCADE,
    pseudonyme VARCHAR(50) NOT NULL,
    hashed_pin VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des compétences
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name JSONB NOT NULL,  -- {fr: "Mathématiques", en: "Math"}
    description JSONB,
    level INTEGER NOT NULL,
    parent_id UUID REFERENCES skills(id) ON DELETE SET NULL
);
```

---

## Implémentation

### Structure SQLAlchemy

```python
# models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()

class BaseModel:
    """Base model avec champs communs"""
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

# models/user.py
from .base import Base, BaseModel

class Parent(Base, BaseModel):
    __tablename__ = "auth_parents"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    
    children = relationship("Child", back_populates="parent")

class Child(Base, BaseModel):
    __tablename__ = "auth_children"
    
    parent_id = Column(UUID(as_uuid=True), ForeignKey("auth_parents.id"), nullable=False)
    pseudonyme = Column(String(50), nullable=False)
    hashed_pin = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    
    parent = relationship("Parent", back_populates="children")
```

### Configuration async

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Mauvaise performance | Faible | Élevé | Indexation, optimisation des requêtes |
| Schéma mal conçu | Moyenne | Élevé | Review des migrations, tests |
| Problèmes de concurrency | Faible | Élevé | Connection pooling, transactions |
| Migration complexe | Moyenne | Moyen | Alembic, scripts de migration |

---

## Références

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/14/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [asyncpg Documentation](https://www.psycopg.org/psycopg3/docs/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Comparaison des SGBD

| Critère | PostgreSQL | MySQL | SQLite | MongoDB | Neo4j |
|---------|------------|-------|--------|--------|-------|
| Type | Relationnel | Relationnel | Relationnel | NoSQL | Graph |
| Transactions | ✅ ACID | ✅ ACID | ⚠️ Limité | ❌ Non | ✅ ACID |
| Performance | ✅ 10/10 | ✅ 9/10 | ⚠️ 7/10 | ✅ 9/10 | ⚠️ 8/10 |
| Requêtes complexes | ✅ 10/10 | ✅ 9/10 | ⚠️ 6/10 | ❌ 4/10 | ✅ 10/10 |
| Relations | ✅ 10/10 | ✅ 9/10 | ⚠️ 7/10 | ❌ 3/10 | ✅ 10/10 |
| JSON | ✅ 10/10 | ⚠️ 7/10 | ⚠️ 6/10 | ✅ 10/10 | ⚠️ 6/10 |
| Async | ✅ 10/10 | ❌ 4/10 | ⚠️ 6/10 | ✅ 9/10 | ⚠️ 7/10 |
| Production | ✅ 10/10 | ✅ 10/10 | ❌ 3/10 | ✅ 10/10 | ⚠️ 7/10 |

### Bonnes pratiques

1. **Indexer les colonnes** fréquemment queryées
2. **Utiliser les constraints** (UNIQUE, NOT NULL, etc.)
3. **Éviter N+1 queries** avec joinedload ou selectinload
4. **Utiliser les transactions** pour les opérations multi-étapes
5. **Migrer par petites étapes** avec Alembic
6. **Backuper régulièrement** la base de données
7. **Monitorer les performances** avec pg_stat_statements
8. **Optimiser les requêtes** avec EXPLAIN ANALYZE
