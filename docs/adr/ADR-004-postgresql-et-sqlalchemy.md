# ADR-004 : PostgreSQL et SQLAlchemy 2 pour la Persistance

## Statut

✅ **Accepted** - Décision validée et implémentée, amendée le 14 août 2026 après la
sous-étape 07.1.

---

## Amendement du 14 août 2026

**Le choix de PostgreSQL, de SQLAlchemy 2 et d'Alembic n'est pas remis en cause.**
Cet amendement ne porte que sur l'esquisse du modèle de compétences, qui figurait
dans la section « Schéma exemple » et que l'implémentation n'a pas suivie.

### Ce qui était esquissé

Une table unique `skills`, auto-référencée par `parent_id`, dont un niveau, une
matière, un domaine et une compétence auraient tous été des lignes, distinguées
par une colonne `level` entière, avec des libellés en JSONB multilingue.

### Ce qui est implémenté

**Quatre tables explicites**, `ref_levels`, `ref_subjects`, `ref_domains` et
`ref_competencies`, plus `ref_competency_prerequisites` pour l'arbre de prérequis.
Trois raisons :

- la fiche 07.1 nomme quatre concepts distincts, et un schéma qui les nomme dit ce
  qu'il modélise ;
- les lectures filtrées et paginées de 07.3 deviennent des jointures directes, là
  où un arbre générique obligerait chaque requête à deviner à quel étage elle se
  trouve ;
- rien n'empêchait, dans l'esquisse, de ranger une matière sous une compétence.
  Une hiérarchie sans étages nommés n'a pas de forme que la base puisse défendre.

Le libellé est du texte simple et non du JSONB multilingue : le MVP est
francophone, et l'internationalisation ajouterait un niveau d'indirection à chaque
lecture pour un besoin qui n'existe pas encore.

**Le référentiel est de plus versionné dans son ensemble.** Une entité
`ref_versions` porte chaque édition, avec les statuts `draft`, `published` et
`archived`, une seule édition publiée à la fois. Chaque ligne fille répète le
`version_id` de son parent et le référence par une clé étrangère composite, ce qui
interdit à une compétence d'emprunter un domaine ou un niveau d'une autre édition.
C'est ce qui protège les traces des étapes 10 à 12 : réimporter un programme crée
une édition au lieu de changer rétroactivement le sens des résultats enregistrés.

Le graphe de prérequis reste la raison pour laquelle PostgreSQL a été préféré à
une base documentaire, et la raison pour laquelle Neo4j avait été envisagé puis
écarté. Cet amendement ne change rien à cet arbitrage : les arêtes vivent dans une
table de liens, interrogée par des jointures et des CTE récursives.

La mise en œuvre est décrite dans `docs/backend/referentiel-competences.md`.

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

-- Référentiel scolaire, versionné dans son ensemble.
-- Remplace l'esquisse `skills` auto-référencée, voir l'amendement du 14 août 2026.
CREATE TABLE ref_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    label VARCHAR(200) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'archived'))
);

-- Une seule édition en vigueur à la fois, autant de brouillons et d'archives
-- que nécessaire.
CREATE UNIQUE INDEX uq_ref_versions_single_published
    ON ref_versions (status) WHERE status = 'published';

CREATE TABLE ref_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID NOT NULL REFERENCES ref_versions(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    label VARCHAR(200) NOT NULL,
    position INTEGER NOT NULL,
    UNIQUE (version_id, code),
    -- Cible des clés étrangères composites ci-dessous.
    UNIQUE (id, version_id)
);

-- ref_subjects suit le même modèle, et ref_domains y ajoute
-- FOREIGN KEY (subject_id, version_id) REFERENCES ref_subjects (id, version_id).

CREATE TABLE ref_competencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID NOT NULL,
    domain_id UUID NOT NULL,
    level_id UUID NOT NULL,
    code VARCHAR(50) NOT NULL,
    label VARCHAR(200) NOT NULL,
    description TEXT,
    position INTEGER NOT NULL,
    UNIQUE (version_id, code),
    UNIQUE (id, version_id),
    -- La version voyage avec la référence : une compétence ne peut pas
    -- emprunter un domaine ou un niveau d'une autre édition.
    FOREIGN KEY (domain_id, version_id)
        REFERENCES ref_domains (id, version_id) ON DELETE CASCADE,
    FOREIGN KEY (level_id, version_id)
        REFERENCES ref_levels (id, version_id) ON DELETE CASCADE
);

-- L'arbre de compétences, une arête par prérequis.
CREATE TABLE ref_competency_prerequisites (
    competency_id UUID NOT NULL,
    prerequisite_id UUID NOT NULL,
    version_id UUID NOT NULL,
    PRIMARY KEY (competency_id, prerequisite_id),
    CHECK (competency_id <> prerequisite_id),
    FOREIGN KEY (competency_id, version_id)
        REFERENCES ref_competencies (id, version_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id, version_id)
        REFERENCES ref_competencies (id, version_id) ON DELETE CASCADE
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

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |
| 2026-08-14 | Claude Code | Amendement après la sous-étape 07.1 : le référentiel est modélisé par quatre tables explicites et versionné dans son ensemble, à la place de l'esquisse `skills` auto-référencée |
