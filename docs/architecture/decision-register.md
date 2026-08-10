# Registre des Décisions d'Architecture (ADR Register)

> **Dernière mise à jour : 10 août 2026**
> **Statut : En construction**

Ce document est le **registre central** de toutes les Architecture Decision Records (ADR) du projet StudentConnect. Chaque ADR documente une décision architecturale structurante prise par l'équipe.

---

## Comment utiliser ce registre

1. **Pour les développeurs** : Consulter ce registre avant de prendre une décision architecturale
2. **Pour les nouveaux membres** : Lire tous les ADR pour comprendre l'architecture du projet
3. **Pour les reviewers** : Vérifier que les PR respectent les décisions existantes
4. **Pour les maintainers** : Mettre à jour ce registre après chaque nouvelle décision

---

## Structure des dossiers

```
docs/
├── adr/
│   ├── ADR-000-licence-projet.md      # Licence du projet (Proposed)
│   ├── ADR-001-monorepo.md            # À créer
│   ├── ADR-002-nextjs-et-tailwind.md  # À créer
│   ├── ADR-003-fastapi-rest.md        # À créer
│   ├── ADR-004-postgresql-et-sqlalchemy.md # À créer
│   ├── ADR-005-sessions-familiales.md # À créer
│   ├── ADR-006-h5p-standalone.md      # À créer
│   ├── ADR-007-phet-iframe.md         # À créer
│   ├── ADR-008-s3-et-urls-presignees.md # À créer
│   ├── ADR-009-redis-et-celery.md     # À créer
│   └── ADR-010-planning-markdown.md   # À créer
└── architecture/
    ├── decision-register.md           # Ce fichier
    └── diagrams/                       # Diagrammes d'architecture
```

---

## Légende des statuts

| Statut | Description | Emoji |
|--------|-------------|-------|
| Accepted | Décision validée et implémentée | ✅ |
| Proposed | Décision proposée, en discussion | ⚠️ |
| Deprecated | Décision obsolète, remplacée | ❌ |
| Rejected | Décision rejetée | ⛔ |
| Superseeded | Décision remplacée par une nouvelle | 🔄 |

---

## Liste des ADR

### ADR-000 : Licence du projet

| Champ | Valeur |
|-------|--------|
| **Titre** | Choix de la licence du projet StudentConnect |
| **Statut** | ⚠️ Proposed |
| **Date** | 2026-08-10 |
| **Auteur** | Mistral Vibe |
| **Décision** | AGPL-3.0 (en discussion) |
| **Fichier** | [docs/adr/ADR-000-licence-projet.md](../adr/ADR-000-licence-projet.md) |
| **Dépendances** | Aucune |
| **Impact** | Projet entier |

**Résumé** : Proposition d'utiliser la licence AGPL-3.0 pour protéger le code source tout en permettant une utilisation libre pour les établissements éducatifs.

**Statut actuel** : En discussion. Décision finale à valider avec l'équipe et éventuellement un expert juridique.

---

### ADR-001 : Monorepo

| Champ | Valeur |
|-------|--------|
| **Titre** | Architecture Monorepo pour StudentConnect |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-001-monorepo.md](../adr/ADR-001-monorepo.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Structure du projet |

**Résumé** : Décision d'utiliser une architecture monorepo avec Turborepo, pnpm ou équivalent pour gérer frontend, backend, packages et infrastructure.

**Contenu prévu** :
- Justification du choix monorepo vs polyrepo
- Structure des dossiers (apps/, packages/, infrastructure/)
- Outils de gestion (Turborepo, pnpm, etc.)
- Avantages : partage de code, dépendances unifiées, CI/CD simplifiée
- Inconvénients : complexité initiale, taille du dépôt

---

### ADR-002 : Next.js et Tailwind

| Champ | Valeur |
|-------|--------|
| **Titre** | Choix de Next.js 16 et Tailwind CSS 4 pour le frontend |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-002-nextjs-et-tailwind.md](../adr/ADR-002-nextjs-et-tailwind.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Frontend |

**Résumé** : Décision d'utiliser Next.js 16 avec App Router et Tailwind CSS 4 pour le développement frontend.

**Contenu prévu** :
- Justification de Next.js vs autres frameworks (React seul, Vue, Svelte, etc.)
- Avantages de l'App Router
- Choix de Tailwind CSS vs autres solutions (Bootstrap, Chakra, etc.)
- Stack complémentaire : React, TypeScript, Radix UI, etc.
- Bibliothèques additionnelles : TanStack Query, Zustand, React Hook Form, Zod

---

### ADR-003 : FastAPI REST

| Champ | Valeur |
|-------|--------|
| **Titre** | Choix de FastAPI pour le backend avec architecture REST |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-003-fastapi-rest.md](../adr/ADR-003-fastapi-rest.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Backend |

**Résumé** : Décision d'utiliser FastAPI avec Python pour le backend, avec une architecture REST plutôt que GraphQL.

**Contenu prévu** :
- Justification de FastAPI vs Django, Flask, etc.
- Avantages de FastAPI : performance, typage, documentation auto
- Choix de REST vs GraphQL
- Structure du backend (modular monolith)
- Pydantic pour la validation

---

### ADR-004 : PostgreSQL et SQLAlchemy

| Champ | Valeur |
|-------|--------|
| **Titre** | Choix de PostgreSQL avec SQLAlchemy 2 et Alembic |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-004-postgresql-et-sqlalchemy.md](../adr/ADR-004-postgresql-et-sqlalchemy.md) (à créer) |
| **Dépendances** | ADR-003 |
| **Impact** | Persistance |

**Résumé** : Décision d'utiliser PostgreSQL comme base de données principale avec SQLAlchemy 2 comme ORM et Alembic pour les migrations.

**Contenu prévu** :
- Justification de PostgreSQL vs MySQL, MongoDB, Neo4j, etc.
- Avantages de SQLAlchemy 2
- Configuration d'Alembic pour les migrations
- Schéma de base de données

---

### ADR-005 : Sessions familiales

| Champ | Valeur |
|-------|--------|
| **Titre** | Gestion des sessions familiales (Parent + Enfants) |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-005-sessions-familiales.md](../adr/ADR-005-sessions-familiales.md) (à créer) |
| **Dépendances** | ADR-003, ADR-004 |
| **Impact** | Authentification |

**Résumé** : Décision sur le système d'authentification et de gestion des sessions pour les familles (parents et enfants).

**Contenu prévu** :
- Modèle de données : Parent, Enfant, Famille
- Authentification parent : email + mot de passe + vérification email
- Authentification enfant : profil rattaché + pseudonyme + PIN haché
- Sessions : cookies opaques, HttpOnly, Secure, SameSite
- Stockage des sessions : Redis

---

### ADR-006 : H5P Standalone et origine isolée

| Champ | Valeur |
|-------|--------|
| **Titre** | Intégration de H5P via h5p-standalone avec origine isolée |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-006-h5p-standalone.md](../adr/ADR-006-h5p-standalone.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Contenus |

**Résumé** : Décision d'utiliser h5p-standalone pour la lecture de H5P avec une origine de contenu isolée.

**Contenu prévu** :
- Justification de h5p-standalone vs éditeur H5P complet
- Architecture : lecture native sans redirection
- Pipeline : upload, quarantaine, scan, validation, extraction versionnée
- Capture xAPI via dispatcher et bridge postMessage
- Types H5P autorisés dans le MVP

---

### ADR-007 : PhET iframe

| Champ | Valeur |
|-------|--------|
| **Titre** | Intégration des simulations PhET via iframe |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-007-phet-iframe.md](../adr/ADR-007-phet-iframe.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Contenus |

**Résumé** : Décision d'intégrer les simulations PhET via des iframes sécurisées.

**Contenu prévu** :
- Justification de l'approche iframe
- Sélection des simulations : HTML5 françaises uniquement
- Vérification de l'attribution et de la licence
- Isolation de l'origine de contenu
- Preuve finale via mini-test StudentConnect

---

### ADR-008 : S3 et URLs présignées

| Champ | Valeur |
|-------|--------|
| **Titre** | Stockage compatible S3 avec URLs présignées |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-008-s3-et-urls-presignees.md](../adr/ADR-008-s3-et-urls-presignees.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Stockage |

**Résumé** : Décision d'utiliser un stockage compatible S3 avec des URLs présignées pour l'accès aux fichiers.

**Contenu prévu** :
- Justification du stockage objet vs filesystem
- Choix de S3 compatible (AWS S3, DigitalOcean Spaces, MinIO, etc.)
- Architecture : CDN ou origine de contenu dédiée
- Sécurité : URLs présignées avec durée limitée
- Gestion des paquets H5P versionnés

---

### ADR-009 : Redis et Celery

| Champ | Valeur |
|-------|--------|
| **Titre** | Utilisation de Redis et Celery pour les tâches asynchrones |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-009-redis-et-celery.md](../adr/ADR-009-redis-et-celery.md) (à créer) |
| **Dépendances** | ADR-003 |
| **Impact** | Tâches asynchrones |

**Résumé** : Décision d'utiliser Redis comme broker et Celery pour la gestion des tâches asynchrones.

**Contenu prévu** :
- Justification de Celery vs autres solutions (RQ, huey, etc.)
- Architecture : worker(s) Celery avec Redis comme broker
- Cas d'usage : upload H5P, processing,antaine, etc.
- Configuration : queues, retry, scheduling
- Monitoring : Flower ou équivalent

---

### ADR-010 : Planning Markdown sans GitHub Project

| Champ | Valeur |
|-------|--------|
| **Titre** | Pilotage via planning Markdown plutôt que GitHub Project |
| **Statut** | ⏳ À créer |
| **Date** | - |
| **Auteur** | - |
| **Décision** | À décider |
| **Fichier** | [docs/adr/ADR-010-planning-markdown.md](../adr/ADR-010-planning-markdown.md) (à créer) |
| **Dépendances** | Aucune |
| **Impact** | Pilotage |

**Résumé** : Décision de ne pas utiliser GitHub Project mais un planning Markdown simple pour le suivi des tâches.

**Contenu prévu** :
- Justification du choix (simplicité, transparence, contrôle)
- Avantages : versionnable, lisible, indépendant des outils
- Inconvénients : moins visuel, pas de drag-and-drop
- Structure du fichier PLANNING.md
- Processus de mise à jour

---

## Statistiques

| Statut | Count |
|--------|-------|
| ✅ Accepted | 0 |
| ⚠️ Proposed | 1 |
| ⏳ À créer | 9 |
| ❌ Deprecated | 0 |
| ⛔ Rejected | 0 |
| 🔄 Superseeded | 0 |
| **Total** | **10** |

---

## Comment créer un nouvel ADR

1. **Vérifier** qu'aucune décision existante ne couvre déjà le sujet
2. **Discuter** avec l'équipe avant de rédiger
3. **Utiliser le template** ADR (à créer dans docs/adr/TEMPLATE.md)
4. **Numérotation** : Utiliser le prochain numéro disponible
5. **Statut initial** : `Proposed`
6. **Créer un PR** avec le nouvel ADR
7. **Discuter et valider** avec l'équipe
8. **Mettre à jour** le statut en `Accepted` une fois validé
9. **Mettre à jour** ce registre

---

## Bonnes pratiques pour les ADR

1. **Un ADR par décision** : Une seule décision majeure par document
2. **Contexte clair** : Expliquer le problème et les contraintes
3. **Options évaluées** : Présenter au moins 2-3 alternatives
4. **Justification solide** : Expliquer pourquoi une option a été choisie
5. **Conséquences documentées** : Impact positif et négatif
6. **Références** : Lier vers les ressources pertinentes
7. **Historique** : Garder une trace des changements
8. **Revue régulière** : Vérifier si les décisions sont toujours valides

---

## Liens utiles

- [Documentation ADR](https://adr.github.io/)
- [Template ADR de MADR](https://adr.github.io/madr/)
- [Exemples d'ADR](https://github.com/joel-costigliola/architecture-decision-record)
- [Pourquoi documenter les décisions d'architecture ?](https://www.infoq.com/articles/architecture-decision-records/)

---

*Ce registre doit être mis à jour après chaque nouvelle décision architecturale.*
