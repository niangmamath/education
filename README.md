# StudentConnect

> **Plateforme EdTech B2C pour élèves de 6 à 11 ans et leurs parents**
> 
> *Score de santé académique, détection de lacunes, Quick Repairs déterministes*

---

## Produit

StudentConnect est une plateforme éducative innovante qui permet aux parents de suivre la santé académique de leurs enfants (6-11 ans) et aux élèves de combler leurs lacunes via des parcours de remédiation personnalisés.

### Fonctionnalités clés

- **Dashboards distincts** : Espace Parent avec score de santé académique et espace Élève gamifié
- **Quick Repairs** : Exercices courts (3-7 minutes) ciblant les lacunes détectées
- **Arbre de compétences** : Modélisation des prérequis et dépendances entre compétences
- **Détection de lacunes** : Identification automatique des lacunes localisées et générales
- **Contenus interactifs** : Lecture native de H5P et intégration de simulations PhET
- **Preuves d'apprentissage** : Capture xAPI des interactions avec les contenus

### Score de santé académique

Un indicateur explicable (non comparatif) basé sur :
- Résultats aux diagnostics internes
- Progression dans les compétences
- Historique des lacunes comblées
- Engagement avec les contenus

---

## Stack Technique

### Architecture

```
Next.js Web (Frontend)
    │ REST/HTTPS
    ▼
FastAPI modular monolith (Backend)
    ├── PostgreSQL (données relationnelles)
    ├── Redis (sessions, cache)
    ├── Celery (tâches asynchrones)
    └── S3-compatible (stockage objet)

Content origin isolée
    ├── h5p-standalone (lecture H5P)
    └── paquets H5P versionnés

PhET
    └── iframe française sécurisée
```

### Frontend

- **Framework** : Next.js 16 (App Router)
- **Langage** : TypeScript strict
- **UI** : Tailwind CSS 4, Radix UI, Lucide React, Framer Motion
- **Data** : TanStack Query, Zustand
- **Forms** : React Hook Form, Zod
- **i18n** : next-intl
- **Charts** : Recharts

### Backend

- **Framework** : FastAPI
- **Langage** : Python 3.11+
- **ORM** : SQLAlchemy 2, Alembic (migrations)
- **Validation** : Pydantic
- **Base de données** : PostgreSQL
- **Cache** : Redis
- **Task Queue** : Celery

### Contenus et Stockage

- **H5P** : h5p-standalone pour lecture native
- **Stockage** : Compatible S3 avec URLs présignées
- **CDN** : Origine de contenu dédiée pour isolation
- **PhET** : Simulations HTML5 françaises en iframe

### Tests et Infrastructure

- **Tests Backend** : Pytest
- **Tests Frontend** : Vitest, Testing Library
- **Tests E2E** : Playwright
- **Conteneurisation** : Docker Compose
- **CI/CD** : GitHub Actions
- **Sécurité** : HTTPS, reverse proxy, logs structurés

---

## Prérequis

### Logiciels requis

- [Git](https://git-scm.com/) 2.40+
- [Node.js](https://nodejs.org/) 20+
- [Python](https://www.python.org/) 3.11+
- [Docker](https://www.docker.com/) 24+
- [Docker Compose](https://docs.docker.com/compose/) 2.20+

### Espace disque

- Minimum 10 Go disponibles (pour Docker, dépendances, caches)

### Mémoire

- Minimum 8 Go RAM (16 Go recommandé pour développement)

---

## Structure du Projet (Cible)

```
studentconnect/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── app/            # App Router
│   │   ├── components/
│   │   ├── lib/
│   │   ├── styles/
│   │   └── package.json
│   └── api/                 # FastAPI backend
│       ├── main.py
│       ├── models/
│       ├── routes/
│       ├── services/
│       └── requirements.txt
├── packages/
│   ├── ui/                  # Composants partagés
│   ├── schemas/            # Schémas Pydantic/Zod
│   └── config/             # Configuration commune
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile.web
│   │   └── Dockerfile.api
│   ├── nginx/
│   │   └── nginx.conf
│   └── scripts/            # Scripts utilitaires
├── docs/
│   ├── architecture/
│   │   ├── decision-register.md
│   │   └── diagrams/
│   ├── adr/                # Architecture Decision Records
│   ├── api/                # Documentation API
│   ├── security/
│   ├── planning/
│   └── user-guide/
├── steps/                  # Prompts de développement
├── .gitignore
├── .editorconfig
├── .gitattributes
├── .env.example
├── README.md
└── .github/workflows/
    ├── ci.yml
    └── deploy.yml
```

---

## Démarrage Futur

> ⚠️ **En développement** - Les instructions ci-dessous sont la cible pour la phase de développement.

### 1. Cloner le dépôt

```bash
git clone git@github.com:Tidianesarrndiaye-org/StudentConnect.git
cd StudentConnect
```

### 2. Configurer l'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos configurations locales
nano .env  # ou utilisez votre éditeur préféré
```

### 3. Démarrer les conteneurs

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

### 4. Installer les dépendances

```bash
# Frontend
cd apps/web
npm install

# Backend
cd ../api
pip install -r requirements.txt
```

### 5. Initialiser la base de données

```bash
cd apps/api
alembic upgrade head
```

### 6. Démarrer les applications

```bash
# Dans un terminal
cd apps/web
npm run dev

# Dans un autre terminal
cd apps/api
uvicorn main:app --reload --port 8000
```

### 7. Accéder à l'application

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- API Docs : http://localhost:8000/docs

---

## Sécurité

### Principes

- **Zéro donnée réelle** : Toutes les données du stage sont fictives
- **Protection des enfants** : Aucun email ou téléphone requis pour les comptes enfants
- **Sessions sécurisées** : Cookies HttpOnly, Secure, SameSite
- **Stockage des secrets** : Jamais dans le code ou les fichiers trackés
- **Audit régulier** : Vérification des dépendances et configurations

### Bonnes pratiques

- Ne jamais commiter `.env`, secrets, tokens ou clés
- Utiliser des variables d'environnement pour toute configuration sensible
- Valider toutes les entrées utilisateur
- Sanitizer les sorties avant affichage
- Limiter les permissions selon le principe du moindre privilège

### Reporting de vulnérabilités

Voir [SECURITY.md](./SECURITY.md) pour les procédures de reporting.

---

## Statut Actuel

> **📦 Phase : 01 - Gouvernance et Audit**

- ✅ Dépôt vidé et vérifié
- 🔄 Création des fichiers racine en cours
- ⏳ Initialisation du monorepo
- ⏳ Configuration de l'infrastructure locale

### Prochaines étapes

1. ✅ Vérification du dépôt vide (Terminé)
2. 🔄 Création des fichiers racine (En cours)
3. ⏳ Création des ADR initiaux
4. ⏳ Initialisation du workspace monorepo

---

## Contribuer

Voir [CONTRIBUTING.md](./CONTRIBUTING.md) pour les guidelines de contribution.

## Code de conduite

Voir [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) pour nos engagements.

## Licence

Le projet est en cours de décision de licence. Voir [LICENSE](./LICENSE) ou [docs/adr/ADR-000-licence-projet.md](./docs/adr/ADR-000-licence-projet.md) pour plus d'informations.

## Contact

- **Organisation** : [tidianesarrndiaye-org](https://github.com/tidianesarrndiaye-org)
- **Dépôt** : [StudentConnect](https://github.com/Tidianesarrndiaye-org/StudentConnect)

---

*Documentation générée le 10 août 2026*
