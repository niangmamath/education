# StudentConnect

> **Plateforme EdTech B2C pour élèves de 6 à 11 ans et leurs parents**
>
> *Diagnostic hiérarchique par paliers, remédiation ciblée, historique conservé*

---

## Produit

StudentConnect est une plateforme éducative qui permet aux parents de suivre
la santé académique de leurs enfants (6-11 ans) et aux élèves de combler leurs
lacunes via des parcours de remédiation personnalisés. Un enfant n'est jamais
évalué sur tout un programme d'un coup : il est testé palier de compétences
après palier, chaque lacune déclenche une remédiation ciblant le vrai
prérequis en cause, puis un retest confirme l'acquisition avant de débloquer
le palier suivant.

### Fonctionnalités clés

- **Dashboards distincts** : Espace Parent avec score de santé académique et
  espace Élève centré sur les prochaines actions
- **Quick Repairs** : Exercices courts (3-7 minutes) ciblant les lacunes
  détectées, toujours par le vrai prérequis en cause
- **Référentiel versionné** : Compétences, domaines, matières et classes,
  avec un graphe de prérequis pouvant traverser matières et niveaux
- **Diagnostic explicable** : Rien n'est stocké, tout se recalcule à chaque
  lecture, cinq règles nommées et publiées
- **Contenus interactifs** : Lecture native de H5P, fiches de remédiation
  écrites nativement dans la plateforme
- **Preuves d'apprentissage** : Capture xAPI des interactions avec les
  contenus, via une origine de contenu isolée

### Score de santé académique

Un indicateur explicable (non comparatif) basé sur :
- Résultats aux diagnostics internes
- Progression dans les compétences
- Historique des lacunes comblées, pondéré par le nombre de tentatives
- Engagement avec les contenus

---

## Stack technique

### Architecture

```
Next.js Web (Frontend)
    │ REST/HTTPS, appelé depuis les composants serveur
    ▼
FastAPI monolithe modulaire (Backend)
    ├── PostgreSQL (données relationnelles)
    ├── Redis (sessions, cache)
    ├── Celery (tâches asynchrones)
    └── S3-compatible / MinIO (stockage objet)

Origine de contenu isolée (nginx)
    ├── h5p-standalone (lecture H5P)
    └── paquets H5P versionnés par empreinte
```

### Frontend

- **Framework** : Next.js 16 (App Router)
- **Langage** : TypeScript strict
- **UI** : Bootstrap 5.3.8, Lucide React

### Backend

- **Framework** : FastAPI
- **Langage** : Python 3.12+
- **ORM** : SQLAlchemy 2 async, Alembic (migrations)
- **Validation** : Pydantic
- **Base de données** : PostgreSQL 17
- **Cache et sessions** : Redis
- **Task queue** : Celery

### Contenus et stockage

- **H5P** : `h5p-standalone` pour lecture native, huit types autorisés
  (ADR-012), jamais extrait sur disque avant vérification
- **Stockage** : MinIO en local, compatible S3, URLs présignées
- **Isolation** : origine de contenu dédiée servie par nginx, jamais
  l'origine de l'application

### Tests et infrastructure

- **Tests backend** : Pytest, intégration comprise contre PostgreSQL réel
- **Qualité backend** : Ruff, Mypy
- **Qualité frontend** : ESLint, TypeScript
- **Conteneurisation** : Docker Compose
- **CI/CD** : GitHub Actions

---

## Prérequis

### Logiciels requis

- [Git](https://git-scm.com/) 2.40+
- [Node.js](https://nodejs.org/) 20+ et [pnpm](https://pnpm.io/) 11+
- [Python](https://www.python.org/) 3.12+
- [Docker](https://www.docker.com/) 24+ avec Docker Compose 2.20+

### Espace disque et mémoire

- Minimum 10 Go disponibles (Docker, dépendances, caches)
- Minimum 8 Go RAM (16 Go recommandé pour développement)

---

## Structure du projet

```
StudentConnect-dev/
├── apps/
│   ├── web/                     # Next.js frontend
│   │   ├── app/                 # App Router
│   │   ├── components/
│   │   └── lib/
│   └── api/                     # FastAPI backend
│       ├── app/
│       │   ├── api/             # Routes v1
│       │   ├── models/          # Modèles SQLAlchemy
│       │   ├── schemas/         # Schémas Pydantic
│       │   └── <domaine>/       # referential, catalog, assignments,
│       │                        # attempts, diagnostic, xapi, authored...
│       ├── alembic/
│       └── tests/
├── docs/
│   ├── adr/                     # Architecture Decision Records
│   ├── architecture/            # Registre des décisions
│   ├── backend/                 # Référence technique par domaine
│   ├── ux/                      # Parcours, navigation, design system
│   ├── contenus/                # Contenus H5P et fiches à fabriquer
│   └── deploiement/             # Démonstration par tunnel
├── steps/                       # Feuille de route par étape, un dossier
│                                 # numéroté par étape, brouillon tant que
│                                 # l'étape n'est pas ouverte
├── infrastructure/
│   ├── nginx/                   # Configuration de l'origine de contenu
│   └── scripts/                 # check_step03.sh, deployer_h5p.sh...
├── experiments/h5p-spike/       # Spike H5P de l'étape 04, toujours actif
├── docker-compose.dev.yml       # Pile locale de ce worktree de développement
├── .env.example
└── .github/workflows/
```

---

## Démarrage

```bash
git clone git@github.com:Tidianesarrndiaye-org/StudentConnect.git
cd StudentConnect

cp .env.example .env
# éditer .env avec vos configurations locales

pnpm install --recursive

docker compose -f docker-compose.dev.yml up -d
./infrastructure/scripts/create_minio_buckets.sh

cd apps/api
alembic upgrade head
cd ../..

pnpm dev
```

- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- API Docs : http://localhost:8000/docs

---

## Sécurité

### Principes

- **Zéro donnée réelle** : toutes les données de démonstration sont fictives,
  préfixées `demo-` et recréées par `python -m app.demo`
- **Protection des enfants** : aucun email ni téléphone requis pour un compte
  Enfant, connexion par code famille et PIN
- **Sessions sécurisées** : cookies `HttpOnly`, `Secure`, `SameSite`, sessions
  opaques en Redis, jamais en SQL
- **Stockage des secrets** : jamais dans le code ou les fichiers trackés

### Bonnes pratiques

- Ne jamais commiter `.env`, secrets, tokens ou clés
- Utiliser des variables d'environnement pour toute configuration sensible
- Valider toutes les entrées utilisateur

### Reporting de vulnérabilités

Voir [SECURITY.md](./SECURITY.md) pour les procédures de reporting.

---

## Statut actuel

La boucle complète du MVP est fonctionnelle et éprouvée sur la pile vivante :
inscription, examen d'entrée par palier de compétences, diagnostic
explicable, remédiation ciblée par prérequis, retest, tableaux de bord Parent
et Élève. L'état détaillé, étape par étape, vit dans
[`steps/ETAT.md`](./steps/ETAT.md) ; la feuille de route à venir vit dans
[`steps/PLANNING.md`](./steps/PLANNING.md).

---

## Contribuer

Voir [CONTRIBUTING.md](./CONTRIBUTING.md) pour les guidelines de contribution.

## Code de conduite

Voir [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) pour nos engagements.

## Licence

Le projet est en cours de décision de licence. Voir [LICENSE](./LICENSE) ou
[docs/adr/ADR-000-licence-projet.md](./docs/adr/ADR-000-licence-projet.md)
pour plus d'informations.

## Contact

- **Organisation** : [tidianesarrndiaye-org](https://github.com/tidianesarrndiaye-org)
- **Dépôt** : [StudentConnect](https://github.com/Tidianesarrndiaye-org/StudentConnect)
