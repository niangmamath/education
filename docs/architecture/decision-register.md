# Registre des Décisions d'Architecture (ADR Register)

> **Dernière mise à jour : 25 août 2026**
> **Statut : à jour, reconstruit depuis les fichiers d'ADR**

Ce document est le **registre central** de toutes les Architecture Decision Records (ADR) du projet StudentConnect. Chaque ADR documente une décision architecturale structurante prise par l'équipe.

---

## Comment utiliser ce registre

1. **Pour les développeurs** : Consulter ce registre avant de prendre une décision architecturale
2. **Pour les nouveaux membres** : Lire tous les ADR pour comprendre l'architecture du projet
3. **Pour les reviewers** : Vérifier que les PR respectent les décisions existantes
4. **Pour les maintainers** : Mettre à jour ce registre après chaque nouvelle décision

---

## Structure des dossiers

Les vingt-deux ADR existent toutes en fichier ; ce registre les résume et ne
les remplace pas.

```
docs/
├── adr/
│   ├── ADR-000-licence-projet.md              # Licence du projet
│   ├── ADR-001-monorepo.md                    # Monorepo pnpm et Turborepo
│   ├── ADR-002-nextjs-et-tailwind.md          # Next.js, App Router, Bootstrap
│   ├── ADR-003-fastapi-rest.md                # FastAPI et REST
│   ├── ADR-004-postgresql-et-sqlalchemy.md    # PostgreSQL, SQLAlchemy, référentiel
│   ├── ADR-005-sessions-familiales.md         # Sessions Redis et unicité familiale
│   ├── ADR-006-h5p-standalone.md              # H5P sans serveur H5P
│   ├── ADR-007-phet-iframe.md                 # PhET en iframe
│   ├── ADR-008-s3-et-urls-presignees.md       # Stockage privé et URLs signées
│   ├── ADR-009-redis-et-celery.md             # Redis et Celery
│   ├── ADR-010-planning-markdown.md           # Planning en Markdown
│   ├── ADR-011-sqlalchemy-async.md            # SQLAlchemy async et asyncpg
│   ├── ADR-012-h5p-standalone-pilote.md       # Types H5P autorisés, accepté sous conditions
│   ├── ADR-013-catalogue-lie-par-code.md      # Catalogue lié par code métier
│   ├── ADR-014-ingestion-xapi.md              # Ingestion xAPI, acteur pseudonyme, prééminence
│   ├── ADR-015-diagnostic-explicable.md       # Diagnostic explicable et non stocké
│   ├── ADR-016-web-parle-a-l-api-par-le-serveur.md  # Le web appelle l’API par son serveur
│   ├── ADR-017-fiches-de-remediation-ecrites-ici.md # Fiches de remédiation écrites ici
│   ├── ADR-018-six-classes-cumulatives.md      # Six classes cumulatives, un examen par classe
│   ├── ADR-019-anglais-et-trois-questions-par-competence.md # Anglais, prérequis inter-matières
│   ├── ADR-020-rotation-des-questions-de-fiche.md # Rotation des questions de fiche
│   └── ADR-021-evaluation-par-paliers.md       # Évaluation par paliers, bornée à la classe
└── architecture/
    └── decision-register.md                   # Ce fichier
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
| **Titre** | Licence du projet |
| **Statut** | ⚠️ **Proposed** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Licence à arrêter avant publication |
| **Fichier** | [docs/adr/ADR-000-licence-projet.md](../adr/ADR-000-licence-projet.md) |
| **Dépendances** | Aucune |
| **Impact** | Juridique |

**Résumé** : Choix de la licence sous laquelle le projet est publié. Seule ADR encore ouverte.

---

### ADR-001 : Monorepo

| Champ | Valeur |
|-------|--------|
| **Titre** | Monorepo |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Monorepo pnpm et Turborepo |
| **Fichier** | [docs/adr/ADR-001-monorepo.md](../adr/ADR-001-monorepo.md) |
| **Dépendances** | Aucune |
| **Impact** | Structure |

**Résumé** : Un seul dépôt pour le web, l'API et les paquets partagés.

---

### ADR-002 : Next.js et design system

| Champ | Valeur |
|-------|--------|
| **Titre** | Next.js et design system |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Next.js 16, App Router |
| **Fichier** | [docs/adr/ADR-002-nextjs-et-tailwind.md](../adr/ADR-002-nextjs-et-tailwind.md) |
| **Dépendances** | ADR-001 |
| **Impact** | Frontend |

**Résumé** : Next.js et App Router. Tailwind, retenu à l'origine, a été remplacé par Bootstrap 5.3.8 à l'étape 05.

---

### ADR-003 : FastAPI REST

| Champ | Valeur |
|-------|--------|
| **Titre** | FastAPI REST |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | FastAPI, REST, monolithe modulaire |
| **Fichier** | [docs/adr/ADR-003-fastapi-rest.md](../adr/ADR-003-fastapi-rest.md) |
| **Dépendances** | ADR-001 |
| **Impact** | Backend |

**Résumé** : API REST servie par un monolithe modulaire FastAPI, sans GraphQL ni microservices.

---

### ADR-004 : PostgreSQL et SQLAlchemy

| Champ | Valeur |
|-------|--------|
| **Titre** | PostgreSQL et SQLAlchemy |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026, amendée le 14 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | PostgreSQL 17, SQLAlchemy 2, Alembic |
| **Fichier** | [docs/adr/ADR-004-postgresql-et-sqlalchemy.md](../adr/ADR-004-postgresql-et-sqlalchemy.md) |
| **Dépendances** | ADR-003 |
| **Impact** | Données |

**Résumé** : Amendée à l'étape 07 : l'esquisse d'une table `skills` unique auto-référencée est remplacée par quatre tables explicites et un référentiel versionné.

---

### ADR-005 : Sessions familiales

| Champ | Valeur |
|-------|--------|
| **Titre** | Sessions familiales |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026, amendée le 14 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Sessions opaques en Redis, jamais en SQL |
| **Fichier** | [docs/adr/ADR-005-sessions-familiales.md](../adr/ADR-005-sessions-familiales.md) |
| **Dépendances** | ADR-003, ADR-009 |
| **Impact** | Sécurité |

**Résumé** : Amendée à l'étape 06 : unicité familiale du pseudonyme, code famille, Argon2id au lieu de bcrypt, plafond sur les tentatives de PIN.

---

### ADR-006 : H5P Standalone et origine isolée

| Champ | Valeur |
|-------|--------|
| **Titre** | H5P Standalone et origine isolée |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | `h5p-standalone`, origine de contenu isolée |
| **Fichier** | [docs/adr/ADR-006-h5p-standalone.md](../adr/ADR-006-h5p-standalone.md) |
| **Dépendances** | ADR-008 |
| **Impact** | Contenus |

**Résumé** : Lecture H5P native, sans serveur H5P complet ni éditeur.

---

### ADR-007 : PhET en iframe

| Champ | Valeur |
|-------|--------|
| **Titre** | PhET en iframe |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Simulations PhET françaises en iframe isolée |
| **Fichier** | [docs/adr/ADR-007-phet-iframe.md](../adr/ADR-007-phet-iframe.md) |
| **Dépendances** | ADR-006 |
| **Impact** | Contenus |

**Résumé** : PhET consommé dans la plateforme, sans redirection.

---

### ADR-008 : S3 et URLs présignées

| Champ | Valeur |
|-------|--------|
| **Titre** | S3 et URLs présignées |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Stockage objet compatible S3, URLs présignées |
| **Fichier** | [docs/adr/ADR-008-s3-et-urls-presignees.md](../adr/ADR-008-s3-et-urls-presignees.md) |
| **Dépendances** | ADR-003 |
| **Impact** | Stockage |

**Résumé** : Cinq buckets privés, aucun accès public direct.

---

### ADR-009 : Redis et Celery

| Champ | Valeur |
|-------|--------|
| **Titre** | Redis et Celery |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Redis pour le cache et les sessions, Celery pour l'asynchrone |
| **Fichier** | [docs/adr/ADR-009-redis-et-celery.md](../adr/ADR-009-redis-et-celery.md) |
| **Dépendances** | ADR-003 |
| **Impact** | Infrastructure |

**Résumé** : Redis porte les sessions et le cache, Celery les tâches de fond.

---

### ADR-010 : Planning Markdown

| Champ | Valeur |
|-------|--------|
| **Titre** | Planning Markdown |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Planning Markdown plutôt que GitHub Project |
| **Fichier** | [docs/adr/ADR-010-planning-markdown.md](../adr/ADR-010-planning-markdown.md) |
| **Dépendances** | Aucune |
| **Impact** | Pilotage |

**Résumé** : Suivi versionné, lisible et indépendant des outils.

---

### ADR-011 : SQLAlchemy async

| Champ | Valeur |
|-------|--------|
| **Titre** | SQLAlchemy async |
| **Statut** | ✅ **Accepted** |
| **Date** | 11 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Engine asynchrone et asyncpg |
| **Fichier** | [docs/adr/ADR-011-sqlalchemy-async.md](../adr/ADR-011-sqlalchemy-async.md) |
| **Dépendances** | ADR-004 |
| **Impact** | Backend |

**Résumé** : L'API sert ses requêtes sur une boucle d'événements ; les commandes en ligne empruntent psycopg2.

---

### ADR-012 : H5P Standalone pour le pilote

| Champ | Valeur |
|-------|--------|
| **Titre** | H5P Standalone pour le pilote |
| **Statut** | ✅ **Accepted sous conditions** |
| **Date** | 13 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Liste blanche de types H5P, tenue par une contrainte en base ; huit types depuis l’amendement du 17 août 2026 |
| **Fichier** | [docs/adr/ADR-012-h5p-standalone-pilote.md](../adr/ADR-012-h5p-standalone-pilote.md) |
| **Dépendances** | ADR-006 |
| **Impact** | Contenus |

**Résumé** : Tout type non listé est refusé par défaut jusqu'à un test et une décision explicites. La contrainte est portée par la base depuis l'étape 08.2. **Amendée le 17 août 2026** : un seul type ne peut pas porter une matière — une dictée doit s'entendre, un rangement doit se manipuler — et la liste passe à huit, dont `H5P.Dictation`, le seul qui paie une dette réelle puisque tout le reste peut déjà être demandé dans une fiche écrite ici. `QuestionSet` reste refusé faute d'attribution par sous-contenu, `ArithmeticQuiz` parce qu'il chronomètre un enfant. La version cesse d'être épinglée : le gel est assuré par l'empreinte, qui distingue deux compilations d'une même version là où une chaîne de version ne le peut pas.

---

### ADR-013 : Catalogue lié par code métier

| Champ | Valeur |
|-------|--------|
| **Titre** | Catalogue lié par code métier |
| **Statut** | ✅ **Accepted** |
| **Date** | 15 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Le catalogue pointe vers les codes de compétences, pas vers leurs lignes |
| **Fichier** | [docs/adr/ADR-013-catalogue-lie-par-code.md](../adr/ADR-013-catalogue-lie-par-code.md) |
| **Dépendances** | ADR-004 |
| **Impact** | Données |

**Résumé** : Le catalogue est un travail éditorial et non une trace : il doit survivre à la publication d'une nouvelle édition du référentiel. Le prix en est un lien sans clé étrangère, contrôlé par une commande dédiée.

---

### ADR-014 : Ingestion xAPI, acteur pseudonyme et prééminence du runtime

| Champ | Valeur |
|-------|--------|
| **Titre** | Ingestion xAPI liée au ticket, acteur pseudonyme, prééminence du runtime |
| **Statut** | ✅ **Accepted** |
| **Date** | 15 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | L'événement est autorisé par le ticket de contenu, l'acteur revendiqué est remplacé par un pseudonyme du serveur, et un événement du runtime prime sur une réponse déclarée |
| **Fichier** | [docs/adr/ADR-014-ingestion-xapi.md](../adr/ADR-014-ingestion-xapi.md) |
| **Dépendances** | ADR-012, ADR-005, ADR-013 |
| **Impact** | Sécurité, Données |

**Résumé** : Le runtime ne reçoit aucune identité, donc rien de ce qu'il nomme dans `actor` n'en est une ; le serveur écrit son propre pseudonyme. L'endpoint exige la session **et** le ticket, et déduit la tentative plutôt que de la laisser nommer. Entre deux récits d'une même question, celui que le serveur a lu lui-même l'emporte. Les agrégats de progrès ne sont pas stockés, pour qu'aucune quatrième chose ne puisse contredire les faits.

---

### ADR-015 : Diagnostic explicable et non stocké

| Champ | Valeur |
|-------|--------|
| **Titre** | Diagnostic explicable, hypothèses non stockées, et ce que chaque côté voit |
| **Statut** | ✅ **Accepted** |
| **Date** | 16 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Les seuils du diagnostic sont publiés, rien n'est stocké, le score résume sans remplacer, et l'Élève voit des actions quand le Parent voit le diagnostic |
| **Fichier** | [docs/adr/ADR-015-diagnostic-explicable.md](../adr/ADR-015-diagnostic-explicable.md) |
| **Dépendances** | ADR-013, ADR-014 |
| **Impact** | Produit, Données |

**Résumé** : Une lacune est une candidate qui porte sa règle et ses comptes ; une compétence jamais travaillée n'en est pas une. Le regroupement ajoute une lecture sans en retirer aucune. Rien n'est stocké, ce qui rend vraie par construction la règle « une cause racine reste une hypothèse jusqu'à la réévaluation ». Le score de santé résume les lectures par compétence sans en remplacer une, et ne compare à personne.

---

### ADR-016 : Le web parle à l'API par son serveur

| Champ | Valeur |
|-------|--------|
| **Titre** | Le web parle à l'API par son serveur, jamais par le navigateur |
| **Statut** | ✅ **Accepted** |
| **Date** | 16 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Le navigateur ne connaît que l'origine du web ; les composants serveur portent le cookie de session jusqu'à l'API |
| **Fichier** | [docs/adr/ADR-016-web-parle-a-l-api-par-le-serveur.md](../adr/ADR-016-web-parle-a-l-api-par-le-serveur.md) |
| **Dépendances** | ADR-002, ADR-005, ADR-012 |
| **Impact** | Frontend, Sécurité |

**Résumé** : Un appel direct depuis le navigateur exigerait un cookie tiers, la forme que les navigateurs suppriment, et exposerait la session à tout ce que la page charge. Les mutations passent par des actions serveur nommées une par une plutôt que par un proxy générique. La seule route d'API du web relaie les événements xAPI du runtime, avec un contrôle d'origine du `postMessage` comme mesure de sécurité de la boucle.

---

### ADR-017 : Les fiches de remédiation sont écrites ici

| Champ | Valeur |
|-------|--------|
| **Titre** | Les fiches de remédiation sont écrites ici, pas importées |
| **Statut** | ✅ **Accepted** |
| **Date** | 17 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Une remédiation est une activité de nature `remediation` écrite dans la plateforme : une leçon, quatre questions, une explication après chacune |
| **Fichier** | [docs/adr/ADR-017-fiches-de-remediation-ecrites-ici.md](../adr/ADR-017-fiches-de-remediation-ecrites-ici.md) |
| **Dépendances** | ADR-012, ADR-013, ADR-015 |
| **Impact** | Contenu, Backend, Frontend |

**Résumé** : Aucune banque ne peut livrer une question rattachée à `cp-ma-denombrer` — ce code est le nôtre — et une preuve qu'on ne peut pas rattacher ne prouve rien. ADR-012 n'autorise qu'une bibliothèque H5P, et l'origine de contenu n'est pas déployable sur Render, où un disque appartient à un seul service. Surtout, une réparation doit enseigner avant d'interroger, ce qu'une question importée ne fait pas. L'examen et les fiches partagent la correction (`authored_questions`) mais pas ce qu'ils répondent : une fiche explique, l'examen se tait, sans quoi il cesserait de mesurer. La route des fiches refuse donc une tentative d'examen, faute de quoi l'examen serait franchissable question par question.

---

### ADR-018 : Six classes cumulatives

| Champ | Valeur |
|-------|--------|
| **Titre** | Six classes cumulatives, un examen par classe, un passage décidé par le parent |
| **Statut** | ✅ **Accepted** |
| **Date** | 18 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | L'élémentaire compte six classes du CI au CM2 ; les compétences sont cumulatives, chaque classe a son examen d'entrée, et le passage est un fait décidé par le parent |
| **Fichier** | [docs/adr/ADR-018-six-classes-cumulatives.md](../adr/ADR-018-six-classes-cumulatives.md) |
| **Dépendances** | ADR-004, ADR-013, ADR-015 |
| **Impact** | Référentiel, Backend, Frontend, Contenu |

**Résumé** : Les niveaux appartiennent à l'édition du référentiel et ne sont pas écrits en dur — une plateforme qui les figerait refuserait de servir un pays qui découpe autrement. Un examen par classe, six questions, parce qu'un examen balayant les six classes ferait trente-six questions à un CM2 et qu'aucun enfant ne le finirait. La classe est déclarée à l'inscription et jamais devinée ; le passage est une ligne d'historique, décidé par le parent, qui monte le palier **sans rien effacer**. Une règle nouvelle, `unobserved-prerequisite`, fait descendre le diagnostic vers les classes antérieures : sans elle, un CM1 qui échoue en division n'aurait aucune lecture sur la multiplication du CE2 et la plateforme proposerait de refaire des divisions — ce que le produit refuse depuis le premier jour.

---

### ADR-019 : Anglais et trois questions par compétence

| Champ | Valeur |
|-------|--------|
| **Titre** | Anglais et trois questions par compétence |
| **Statut** | ✅ **Accepted**, amendée le jour même |
| **Date** | 18 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | L'anglais devient une troisième matière, l'examen passe à trois questions par compétence, des prérequis croisés relient les matières |
| **Fichier** | [docs/adr/ADR-019-anglais-et-trois-questions-par-competence.md](../adr/ADR-019-anglais-et-trois-questions-par-competence.md) |
| **Dépendances** | ADR-004, ADR-018 |
| **Impact** | Référentiel, Contenu |

**Résumé** : Aucune migration, le référentiel modélisait déjà la matière comme une table et le moteur de résultats regroupait déjà plusieurs questions par compétence. Amendée le jour même sur correction du propriétaire : la séparation stricte des trois matières initialement décidée est abandonnée — résoudre un problème de mathématiques suppose de comprendre son énoncé en français, et l'anglais s'appuie sur la mécanique déjà acquise en français. Neuf prérequis croisés ajoutés entre matières, preuve que le graphe de prérequis n'est pas cloisonné par matière.

---

### ADR-020 : Rotation des questions de fiche

| Champ | Valeur |
|-------|--------|
| **Titre** | Rotation des questions de fiche |
| **Statut** | ✅ **Accepted** |
| **Date** | 20 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | Chaque fiche de remédiation passe d'une réserve de quatre à une réserve de huit questions ; quatre sont tirées au hasard à chaque tentative, l'examen n'est pas concerné |
| **Fichier** | [docs/adr/ADR-020-rotation-des-questions-de-fiche.md](../adr/ADR-020-rotation-des-questions-de-fiche.md) |
| **Dépendances** | ADR-017 |
| **Impact** | Contenu, Backend |

**Résumé** : Une fiche reprise montrait les quatre mêmes questions dans le même ordre à chaque tentative. La graine du tirage est l'identifiant de la tentative en cours, stable tant qu'elle reste ouverte, renouvelée à la suivante. `questions_of` reçoit le tirage en paramètre optionnel ; la route de l'examen ne le passe jamais, sur demande explicite du propriétaire — l'examen mesure, il ne doit pas varier d'une tentative à l'autre.

---

### ADR-021 : Évaluation par paliers, bornée à la classe déclarée

| Champ | Valeur |
|-------|--------|
| **Titre** | Évaluation par paliers, bornée à la classe déclarée |
| **Statut** | ✅ **Accepted** |
| **Date** | 25 août 2026 |
| **Auteur** | Équipe StudentConnect |
| **Décision** | L'examen d'entrée sert un palier de compétences prêtes à la fois, jamais toute la classe d'un coup ; un palier reste borné à la classe déclarée, la descente vers une classe antérieure reste réactive |
| **Fichier** | [docs/adr/ADR-021-evaluation-par-paliers.md](../adr/ADR-021-evaluation-par-paliers.md) |
| **Dépendances** | ADR-013, ADR-015, ADR-018, ADR-019 |
| **Impact** | Produit, Référentiel, Backend |

**Résumé** : Correction du propriétaire, 25 août 2026 — un enfant qui valide 100 % à un palier ne reçoit rien de plus à ce palier, juste l'accès au suivant. Aucune migration : `app.referential.graph` partage la lecture du graphe de prérequis entre l'examen et le diagnostic, tout se recalcule à la lecture comme le diagnostic depuis ADR-015. Le seuil de maîtrise est celui qui existe déjà (`RULE_ALL_CORRECT`), sans nouveau seuil inventé. `_root_causes`/`_unobserved_causes` gardent leur marche à un saut, volontairement, le renforcement transitif étant écarté de cette étape.

---

## Statistiques

| Statut | Count |
|--------|-------|
| ✅ Accepted | 21 |
| ⚠️ Proposed | 1 |
| ⏳ À créer | 0 |
| ❌ Deprecated | 0 |
| ⛔ Rejected | 0 |
| 🔄 Superseeded | 0 |
| **Total** | **22** |

Une seule ADR reste ouverte, ADR-000 sur la licence du projet. ADR-012 est
acceptée **sous conditions**, comptée ici parmi les acceptées. Ses huit conditions
sont suivies une par une dans l'ADR elle-même : six sont remplies depuis l'étape
11, deux restent partielles — l'antivirus et la vérification de licence — et
aucune n'est plus entièrement à faire.

---

## Comment créer un nouvel ADR

1. **Vérifier** qu'aucune décision existante ne couvre déjà le sujet
2. **Discuter** avec l'équipe avant de rédiger
3. **Suivre la forme des ADR existantes** : statut, date, décision, conséquences. Aucun template séparé n'est maintenu, les vingt-deux fichiers en tiennent lieu
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
