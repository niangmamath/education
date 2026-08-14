# Prompt général obligatoire pour tous les agents

## 1. Contexte

Tu travailles sur **StudentConnect**, une plateforme EdTech B2C pour les élèves du primaire de 6 à 11 ans et leurs parents. Le projet est réalisé dans le cadre d’un stage présentiel à Casablanca.

Ce projet est totalement distinct d’AgriConnect et de tout travail avec M. Boinzemwendé SANKARA. Ne mélange jamais les documents, acteurs, chemins, contraintes, dépôts ou décisions de ces projets.

- GitHub : `tidianesarrndiaye`
- Dépôt : `StudentConnect`
- Version cible : MVP `V0.1`
- Données du stage : exclusivement fictives
- Utilisateurs principaux : Élève et Parent
- Pilotage : planning Markdown simple

## 2. Vision produit

StudentConnect fournit :

- un dashboard Élève très visuel et gamifié ;
- des Quick Repairs de 3 à 7 minutes ;
- un dashboard Parent avec score de santé académique ;
- des alertes préventives explicables ;
- un arbre de compétences et de prérequis ;
- une détection de lacunes localisées et générales ;
- des contenus H5P lus nativement sans redirection ;
- des simulations PhET françaises dans la plateforme ;
- des vidéos et audios propriétaires ou tiers autorisés ;
- un moteur déterministe de remédiation ;
- une collecte et une projection d’événements xAPI.

## 3. Stack verrouillée

### Frontend

- Next.js 16
- React
- TypeScript strict
- App Router
- Bootstrap 5.3.8
- Radix UI
- Lucide React
- Framer Motion
- Recharts
- TanStack Query
- Zustand
- React Hook Form
- Zod
- next-intl

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Redis
- Celery

### Contenus et stockage

- `h5p-standalone`
- stockage objet compatible S3
- URLs présignées
- CDN ou origine de contenu dédiée
- PhET HTML5 français en iframe isolée

### Tests et infrastructure

- Pytest
- Vitest
- Testing Library
- Playwright
- Docker Compose
- GitHub Actions
- reverse proxy
- HTTPS
- logs structurés

## 4. Choix exclus

Ne pas introduire sans ADR explicite :

- Django ;
- Django REST Framework ;
- Bootstrap ;
- Moodle ;
- CK-12 comme intégration technique ;
- GitHub Project ;
- GraphQL ;
- Neo4j ;
- microservices ;
- application mobile native ;
- éditeur H5P complet ;
- IA générative de diagnostic.

## 5. Règles produit non négociables

- Une note ne remplace jamais une compétence.
- Une observation nouvelle ne doit jamais écraser l’historique.
- Une lacune automatique est une candidate explicable.
- Une lacune générale regroupe des lacunes localisées sans les supprimer.
- Une cause racine reste une hypothèse jusqu’à la réévaluation.
- Une ouverture de contenu ne valide jamais seule une compétence.
- Toute remédiation possède une preuve finale.
- Le score de santé académique doit être explicable et non comparatif.
- Aucun diagnostic médical, psychologique ou comportemental.
- Aucun profilage publicitaire.
- Les comptes enfants n’exigent ni email ni téléphone.
- Les données du stage sont fictives.

## 6. Périmètre MVP

Le MVP doit démontrer :

```text
Parent crée un enfant
→ enfant réalise un diagnostic
→ compétences mises à jour
→ lacune détectée
→ Quick Repair recommandé
→ H5P ou PhET exécuté dans StudentConnect
→ résultat capturé
→ lacune et score recalculés
→ dashboard Parent mis à jour
```

## 7. Architecture attendue

```text
Next.js Web
    │ REST/HTTPS
    ▼
FastAPI modular monolith
    ├── PostgreSQL
    ├── Redis
    ├── Celery
    └── S3-compatible object storage

Content origin isolée
    ├── h5p-standalone
    └── paquets H5P versionnés

PhET
    └── iframe française sécurisée
```

## 8. Monorepo cible

```text
studentconnect/
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   ├── ui/
│   ├── schemas/
│   └── config/
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── api/
│   ├── security/
│   ├── planning/
│   └── user-guide/
├── steps/
├── docker-compose.yml
├── .gitignore
├── .editorconfig
├── .env.example
├── README.md
└── .github/workflows/
```

## 9. Protocole avant action

1. Lire `PROMPT_GENERAL.md`.
2. Lire `DECISIONS_FINALES.md`.
3. Lire `ETAT.md`.
4. Lire le dernier rapport de l’étape précédente.
5. Inspecter réellement le dépôt et `git status`.
6. Vérifier la branche active.
7. Lire toutes les instructions de l’étape courante.
8. Ne travailler que sur la sous-étape assignée.
9. Ne pas inventer les clés, URLs, licences ou résultats techniques.
10. Arrêter et documenter si une décision destructive ou ambiguë bloque le travail.

## 10. Protocole après action

Créer un rapport dans le dossier de l’étape :

```text
rapport_YYYY-MM-DD_HHMM_<slug>.md
```

Le rapport doit utiliser `MODELE_RAPPORT.md` et détailler :

- état initial ;
- fichiers créés ;
- fichiers modifiés ;
- commandes ;
- tests ;
- résultats ;
- décisions ;
- dettes ;
- blocages ;
- mise à jour d’`ETAT.md`.

## 11. Règles anti-conflit

- Ne jamais supprimer un fichier inconnu sans recherche préalable.
- Ne jamais modifier le rapport d’un autre agent.
- Ne jamais réécrire une migration Alembic déjà partagée.
- Ne jamais forcer un push.
- Ne jamais commiter `.env`, secrets, tokens, archives H5P non validées ou données réelles.
- Une seule sous-étape modifiant le schéma de base à la fois.
- En cas de conflit, passer le travail à `Bloqué` et documenter.
- Toute décision structurante crée ou met à jour un ADR.

## 12. Definition of Ready

Une tâche est prête si :

- objectif et valeur compris ;
- prérequis satisfaits ;
- critères d’acceptation vérifiables ;
- données fictives définies ;
- impact de schéma identifié ;
- aucune décision bloquante cachée.

## 13. Definition of Done

Une tâche est terminée si :

- critères d’acceptation passés ;
- tests pertinents exécutés ;
- lint et type-check réussis ;
- sécurité vérifiée selon le périmètre ;
- documentation mise à jour ;
- aucun secret ni donnée réelle ;
- rapport créé ;
- `ETAT.md` mis à jour ;
- prochaine étape explicitée.
