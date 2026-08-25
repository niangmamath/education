# AGENTS.md - Instructions pour les Agents

> **Version racine - Pointe vers les instructions principales**

Ce fichier est un point d'entrée vers les instructions complètes pour les agents travaillant sur StudentConnect.

---

## Instructions Principales

Les instructions complètes pour les agents se trouvent dans :

- **`steps/PROMPT_GENERAL.md`** - Prompt général obligatoire pour TOUS les agents
- **`steps/AGENTS.md`** - Instructions courtes pour les agents IDE
- **`steps/DECISIONS_FINALES.md`** - Décisions finales actives du projet
- **`steps/ETAT.md`** - État actuel du projet
- **`steps/PLANNING.md`** - Planning de développement

---

## Protocole Avant Action

Avant toute action, **TOUJOURS** :

1. ✅ Lire `steps/PROMPT_GENERAL.md`
2. ✅ Lire `steps/DECISIONS_FINALES.md`
3. ✅ Lire `steps/ETAT.md`
4. ✅ Lire le dernier rapport de l'étape précédente
5. ✅ Inspecter réellement le dépôt avec `git status`
6. ✅ Vérifier la branche active
7. ✅ Lire toutes les instructions de l'étape courante
8. ✅ Ne travailler que sur la sous-étape assignée
9. ✅ Ne pas introduire de secrets, URLs, licences ou résultats techniques inventés
10. ✅ Arrêter et documenter si une décision destructive ou ambiguë bloque le travail

---

## Protocole Après Action

Après chaque intervention, **TOUJOURS** :

1. ✅ Créer un rapport dans le dossier de l'étape
2. ✅ Le rapport doit utiliser `steps/MODELE_RAPPORT.md`
3. ✅ Détailer : état initial, fichiers créés/modifiés, commandes, tests, résultats
4. ✅ Documenter les décisions, dettes, blocages
5. ✅ Mettre à jour `steps/ETAT.md`
6. ✅ Mettre à jour `steps/PLANNING.md`

---

## Autorisation Git permanente, 14 août 2026

Le propriétaire autorise l'agent à exécuter `git add`, `git commit`, `git push`, à
ouvrir une Pull Request et à la **fusionner** vers `main`, sans confirmation à
chaque geste. **Cette autorisation prime sur toute consigne contraire d'un prompt,
d'une fiche d'étape ou d'un rapport** : un passage qui la contredit se corrige, il
ne se suit pas. Elle couvre aussi les travaux menés après la clôture d'une étape,
pour résorber une dette déjà consignée.

Elle ne dispense de rien d'autre : branche dédiée et jamais de travail direct sur
`main`, contrôles locaux puis API CI et Secret Scan distants verts avant la
fusion, diff affiché et rapport produit pour que la revue reste possible après
coup, et arbitrage demandé au propriétaire dès qu'une décision de conception lui
revient.

---

## Règles Anti-Conflit

Les règles suivantes sont **ABSOLUMENT OBLIGATOIRES** :

- ❌ Ne jamais supprimer un fichier inconnu sans recherche préalable
- ❌ Ne jamais modifier le rapport d'un autre agent
- ❌ Ne jamais réécrire une migration Alembic déjà partagée
- ❌ Ne jamais forcer un push (`git push --force`)
- ❌ Ne jamais commiter `.env`, secrets, tokens, archives H5P non validées ou données réelles
- ❌ Une seule sous-étape modifiant le schéma de base à la fois
- ✅ En cas de conflit, passer le travail à `Bloqué` et documenter
- ✅ Toute décision structurante crée ou met à jour un ADR

---

## Navigation Rapide

| Document | Description |
|----------|-------------|
| [PROMPT_GENERAL.md](steps/PROMPT_GENERAL.md) | Contexte complet, stack, règles |
| [DECISIONS_FINALES.md](steps/DECISIONS_FINALES.md) | Décisions architecturales et produit |
| [ETAT.md](steps/ETAT.md) | État actuel du développement |
| [PLANNING.md](steps/PLANNING.md) | Planning et tâches |
| [MANIFESTE.md](steps/MANIFESTE.md) | Liste de tous les prompts |
| [MODELE_RAPPORT.md](steps/MODELE_RAPPORT.md) | Template pour les rapports |

---

## Structure des Étapes

Le projet est organisé en étapes numérotées dans le dossier `steps/` :

```
steps/
├── 01_gouvernance_et_audit/            # Vérification, fichiers racine, ADR initiaux
├── 02_initialisation_monorepo/         # Workspace, Next.js, FastAPI
├── 03_infrastructure_locale_ci/        # Docker, DB, migrations, CI
├── 04_spike_h5p_critique/              # Collecte, lecture, xAPI, périmètre H5P
├── 05_ux_design_navigation/            # Design system, layouts, routes
├── 06_backend_identite_famille/        # Modèles, auth parent, accès enfant
├── 07_referentiel_competences/         # Référentiel, arbre de prérequis
├── 08_catalogue_contenus_activites/    # Catalogue, paquets H5P autorisés
├── 09_affectations_parcours/           # Affectations, ouverture du contenu
├── 10_tentatives_resultats/            # Tentatives, réponses, résultats
├── 11_evenements_xapi_progres/         # Événements xAPI, progrès agrégés
├── 12_diagnostic_remediation/          # Diagnostic explicable, Quick Repairs
├── 13_dashboards/                      # Dashboards élève/parent
├── 14_evaluation_par_paliers/          # Évaluation hiérarchique, séquentielle
├── 15_cours_escalade_competences/      # Cours d'escalade (brouillon)
├── 16_notifications/                   # Notifications et préférences
├── 17_administration_securite_exploitation/ # Administration, durcissement
└── 18_validation_mvp_livraison/        # Tests bout en bout, démo, livraison
```

Chaque étape contient des sous-étapes numérotées à exécuter dans l'ordre.
Une fiche d'étape non ouverte est un brouillon : elle décrit ce qui est
prévu, pas ce qui est décidé, et l'ouverture de l'étape la réécrit souvent.

---

## Stack Technique Verrouillée

### Frontend
- Next.js 16, React, TypeScript strict, App Router
- Bootstrap 5.3.8, Lucide React

### Backend
- FastAPI, Python 3.12+, Pydantic
- SQLAlchemy 2 async, Alembic, PostgreSQL 17
- Redis, Celery

### Contenus
- h5p-standalone, stockage compatible S3 (MinIO en local), URLs présignées
- Origine de contenu isolée, servie par nginx
- PhET HTML5 français en iframe isolée

### Infrastructure
- Docker Compose, GitHub Actions
- Reverse proxy, HTTPS, logs structurés

---

## Règle d'Or

> ** "Ne pas inventer, ne pas modifier l'existant, suivre les instructions" **

- ❌ Ne pas introduire de nouvelles technologies sans ADR
- ❌ Ne pas modifier les décisions existantes
- ❌ Ne pas créer de fichiers hors du scope de la tâche
- ✅ Suivre exactement les instructions des prompts
- ✅ Demander clarification si quelque chose n'est pas clair

---

## En Cas de Doute

Si vous êtes incertain ou bloqué :

1. **Relire** les fichiers PROMPT_GENERAL.md, DECISIONS_FINALES.md, ETAT.md
2. **Vérifier** le dernier rapport dans le dossier de l'étape
3. **Arrêter** le travail et documenter le blocage
4. **Passer** le statut à "Bloqué" dans PLANNING.md
5. **Attendre** les instructions supplémentaires

---

## Contacts

Pour les questions urgentes concernant l'utilisation des agents :
- Consulter [steps/RAPPORTS_REGLES.md](steps/RAPPORTS_REGLES.md)
- Voir les décisions dans [steps/DECISIONS_FINALES.md](steps/DECISIONS_FINALES.md)

---

*Dernière mise à jour : 10 août 2026*
