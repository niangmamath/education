# Rapport de réalisation

## Métadonnées

- Étape : prérequis transverse aux étapes 10 et 11
- Sous-étape : runtime de contenu
- Date et heure : 15 août 2026, 16h30
- Agent : Claude Code
- ID du planning : PRE-01
- Branche : `feat/etape-11-runtime-xapi`
- Commit : `cd40620`
- Statut : Terminé

## Objectif

Rendre un paquet H5P vérifié réellement jouable, servi depuis une origine isolée,
sans que le contenu puisse atteindre l'application.

## Prérequis vérifiés

- Étape 09 clôturée, dette résorbée par la Pull Request #17.
- Paquet pilote vérifié et enregistré par 08.2, empreinte conforme à ADR-012.
- Bibliothèques et lecteur préparés par le spike de l'étape 04.
- Rattachement de cette sous-étape à l'étape 11 validé par le propriétaire.

## État initial observé

Une activité pouvait être donnée, commencée et terminée sans que son contenu
puisse être joué. Le paquet vérifié dormait dans un bucket privé ; les
bibliothèques préparées lors du spike vivaient dans `experiments/`, hors du dépôt.

## Travaux réalisés

### La décision : la séparation est la mesure

Un contenu H5P est du JavaScript tiers qui a besoin d'`eval` et de scripts en
ligne pour fonctionner. Le servir depuis l'origine de l'application lui donnerait
les cookies de session et tout ce qui les accompagne, et aucune CSP ne rattrape
cela : le navigateur le considérerait comme faisant partie du site.

L'origine séparée n'est donc pas un durcissement ajouté à une mesure, elle **est**
la mesure. C'est aussi ce qui rend acceptables les `unsafe-inline` et
`unsafe-eval` de sa CSP : ils sont nécessaires au runtime, et ils ne coûtent rien
là où il n'y a rien à prendre.

### Le corollaire : un ticket à la place du cookie

Le cookie de session ne voyage pas jusqu'à l'autre origine — c'est le but. Il
fallait donc autre chose pour dire qu'une requête est autorisée.

Un ticket opaque, frappé quand un enfant ouvre une activité en cours, gardé
trente minutes dans Redis, vérifié par `auth_request` à chaque fichier servi. Il
ne porte aucune identité : il nomme une affectation et le contenu qu'il ouvre.
Rangé sous son empreinte comme une session, si bien que lire Redis apprend quels
contenus sont ouverts, jamais les tickets qui les ouvrent. L'origine, elle,
n'apprend jamais qui est qui : elle demande, et elle obéit.

### Le déploiement

C'est là que l'archive est enfin ouverte, après avoir été vérifiée en 08.2 et
jamais avant. Elle est relue depuis le bucket plutôt que depuis une copie sur
disque, et les contrôles de chemin de l'inspection sont rejoués à l'écriture —
non par méfiance envers le premier contrôle, mais envers l'intervalle entre les
deux.

L'empreinte nomme le dossier, donc redéployer les mêmes octets est idempotent et
deux paquets ne peuvent pas se télescoper. Le volume est monté en lecture seule
dans l'origine : elle sert ce que l'API a déposé et ne peut rien y ajouter.

### Une difficulté rencontrée

La première version passait le ticket à l'API par deux en-têtes calculés dans
nginx. Cela ne fonctionne pas : une sous-requête `auth_request` a son propre
cache de variables, et tout ce que la location protégée calcule arrive vide. L'URL
d'origine entière est passée à la place, et l'API l'analyse — un seul endroit au
lieu de deux, et rien qui puisse être subtilement faux dans un fichier de
configuration.

## Fichiers créés

- `apps/api/app/content/{__init__,tokens,deploy}.py`
- `apps/api/app/content/page/play.html`
- `apps/api/app/api/v1/internal.py`
- `apps/api/tests/test_content_runtime.py`
- `infrastructure/nginx/content-origin.conf`
- `docs/backend/runtime-contenu.md`
- `steps/11_evenements_xapi_progres/00_runtime_contenu.md`

## Fichiers modifiés

- `docker-compose.yml`, service `content` et volume partagé
- `apps/api/app/catalog/{__main__,storage}.py`, verbes de déploiement et `get`
- `apps/api/app/api/v1/assignments.py`, `apps/api/app/schemas/assignment.py`
- `apps/api/app/core/{config,routing}.py`, `.env.example`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`

Aucune migration : rien du schéma n'a changé.

## Commandes exécutées

```
docker compose up -d content api
docker compose exec -T api python -m app.catalog deploy-runtime /tmp/prepared
docker compose exec -T api python -m app.catalog deploy demo-vrai-faux-01
docker compose exec -T api ruff format --check . ; ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api pytest -q
curl sur l'origine de contenu, avec et sans ticket
```

## Tests exécutés

23 tests dédiés : dépôt d'une archive et refus de tout ce qui sort du dossier,
cycle de vie des tickets, et l'endpoint que l'origine interroge.

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 50 fichiers
Pytest     : 397 tests réussis, dont 23 nouveaux
Déploiement: bibliothèques 533 fichiers, lecteur 27 fichiers, inventaire écrit
Déploiement: paquet pilote déployé, 3 fichiers, 1 055 702 octets
Origine    : h5p.json avec ticket 200, bibliothèque avec ticket 200
Origine    : sans ticket 403, ticket d'un autre contenu 403
Origine    : page du lecteur servie sans ticket, CSP et nosniff présents
Tests      : chemin remontant et chemin absolu refusés au déploiement
Tests      : empreinte qui n'en est pas une refusée avant de devenir un dossier
Tests      : archive sans manifeste ne laissant rien derrière elle
Tests      : ticket révoqué, inventé ou pour un autre contenu, refusés
Tests      : Redis ne contient pas le ticket mais son empreinte
```

## Critères d'acceptation

- [x] Contenu servi depuis une origine distincte, avec CSP restrictive.
- [x] Aucun cookie de l'application n'atteint cette origine.
- [x] Accès au contenu vérifié à chaque fichier, sans que l'origine sache qui.
- [x] Déploiement idempotent, refusant tout ce qui sort du dossier cible.
- [x] Bibliothèques figées avec un inventaire de leurs empreintes.
- [x] Formatage, lint, typage et tests verts.

## Décisions ou ADR

Aucune ADR nouvelle : ADR-012 prescrivait déjà l'origine isolée, et cette
sous-étape l'exécute. Le choix du ticket plutôt que d'une autre forme
d'autorisation est consigné ici et dans `docs/backend/runtime-contenu.md`.

## Écarts par rapport au prompt

L'intégration web annoncée avec cette sous-étape n'y figure pas. Le web n'appelle
pas encore l'API, et le faire suppose de régler la session entre deux origines,
ce qui est le sujet de l'étape 13. La promesse a été corrigée plutôt que tenue à
moitié.

## Risques ou dette technique

- Aucune ingestion des événements : la page les remonte par `postMessage`, rien
  ne les reçoit encore. C'est 11.1, et c'était la raison de construire ceci
  d'abord.
- Aucune intégration web, reportée à l'étape 13.
- Aucun antivirus, condition 2 d'ADR-012 pour la production.
- Aucune purge des contenus déployés qui ne servent plus.
- `frame-ancestors` est figé sur `http://localhost:3000` dans la configuration
  nginx ; il devra suivre le domaine réel au déploiement.

## Blocages

Aucun.

## Prochaines actions

1. Étape 10, tentatives et résultats.
2. Puis l'étape 11, dont 11.3 consomme les résultats de 10.3.

## Correction d'ordre

Ce travail avait d'abord été rattaché à l'étape 11, avec un décalage de l'étape
10 après elle. Le décalage était une erreur : 11.3 produit des agrégats « à
partir des événements **et résultats** », et ces résultats sont ceux de 10.3.
L'ordre initial du découpage est rétabli. Le runtime, lui, reste avant les deux :
il est leur prérequis commun.

## Mise à jour appliquée à ETAT.md

Sous-étape 11.0 consignée, prochaine action mise à jour.

## Mise à jour appliquée à PLANNING.md

XAP-00 terminée, XAP-01 en cours.
