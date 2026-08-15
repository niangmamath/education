# Rapport de réalisation

## Métadonnées

- Étape : 11, événements xAPI et progrès
- Sous-étapes : 11.1, 11.2, 11.3 et 11.4
- Date et heure : 15 août 2026, 20h30
- Agent : Claude Code
- ID du planning : XAP-01 à XAP-04
- Branche : `feat/etape-11-xapi`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Recevoir les événements du runtime de contenu, les rattacher à l'Élève sans
jamais exposer son identité au contenu, et agréger les progrès à partir de ces
événements et des résultats de l'étape 10.

## Prérequis vérifiés

- Étape 10 clôturée, dette résorbée, audit de cohérence passé, Pull Request #21,
  commit `1fad608`.
- Migration à `0009_question_attribution`, 441 tests verts.
- Runtime de contenu en place : origine nginx isolée, tickets Redis opaques,
  `play.html` remontant déjà les événements par `postMessage`.
- ADR-012 relue, en particulier sa condition 6, seule condition entièrement à
  faire, et le tableau de suivi ajouté par l'audit.

## État initial observé

Un contenu jouait, émettait des événements xAPI, et personne ne les recevait.
`attempt_responses.source` distinguait `declared` de `xapi` depuis la dette de
l'étape 10, mais aucune ligne ne portait `xapi` et aucune règle ne disait ce qui
primerait entre les deux. La colonne existait ; la décision, non.

## Travaux réalisés

### 11.1, ingestion et validation

Une table `xapi_statements`, migration `0010_xapi_statements` réversible, qui
garde l'événement tel que reçu — acteur déjà remplacé —, son verbe, son objet,
ce que le contenu a conclu, l'horodatage que la source prétend et celui du
serveur.

`POST /api/v1/me/xapi/statements` exige **deux choses à la fois** : la session
Élève, par le cookie, et le ticket de contenu, dans l'en-tête
`X-Content-Ticket`. Le ticket voyage dans un en-tête et non dans le corps parce
qu'il n'est pas une partie de l'événement : un événement qui porterait sa propre
autorisation serait à une falsification près d'être sa propre permission.

**Le client ne nomme jamais la tentative.** Le serveur la déduit du ticket :
ticket → affectation → tentative en cours. Un client capable de la désigner
pourrait déposer une observation sur un autre travail.

La validation refuse plutôt qu'elle ne répare : un événement sans identifiant,
un verbe hors des huit que H5P émet, un objet absent ou trop long pour la
colonne des réponses, un corps de plus de 16 kio, un `result.success` qui n'est
pas un booléen. **Refuser plutôt que tronquer** : raccourcir un identifiant
d'objet fusionnerait silencieusement deux questions en une.

Un rejeu est reconnu : `(attempt_id, statement_id)` est unique, le même
événement renvoyé rend `200` et l'enregistrement déjà tenu. L'unicité est portée
par la tentative et non globale, sinon une famille pourrait faire taire
l'événement d'une autre en réservant son identifiant la première.

L'identifiant est **exigé de l'émetteur**, et `play.html` en pose désormais un
quand le contenu n'en fournit pas. Le frapper côté serveur ferait de chaque
réessai une seconde réponse.

### 11.2, liaison de l'acteur pseudonyme

Quoi que l'événement mette dans `actor`, il ne survit pas à l'ingestion. Le
serveur écrit un agent pseudonyme dont le nom de compte est
`HMAC-SHA256(SECRET_KEY, "xapi-actor:" + identifiant de l'enfant)`.

Le raisonnement tient en une phrase : **le runtime ne reçoit aucune identité**,
donc rien de ce qu'il nomme là n'en est une que nous lui ayons donnée.
Conserver le champ revendiqué laisserait un navigateur écrire un vrai nom dans
la base par un champ que personne ne lit.

Dans l'autre sens, l'URL de lecture ne porte qu'une empreinte de contenu et un
ticket : ni identifiant d'enfant, ni pseudonyme, ni code famille, ni
affectation. C'était déjà vrai depuis `PRE-01` ; c'est désormais **éprouvé par un
test**, parce qu'une propriété d'isolation que personne ne vérifie finit par ne
plus être vraie.

Le lien entre un événement et un enfant est fait sur le serveur, à partir d'une
session, et n'existe nulle part ailleurs.

### 11.3, agrégation des progrès

`GET /api/v1/me/progress` et `GET /api/v1/children/{child_id}/progress`.

**Rien n'est stocké.** Pas de table d'agrégats : les progrès sont calculés à
chaque lecture. C'est ce qui les rend reproductibles au sens que l'étape
demande — les mêmes faits donnent la même réponse, et il n'existe pas une
quatrième chose capable de contredire les trois dont elle est tirée.

**Les résultats sont sommés, jamais recalculés.** La lecture d'une tentative a
été faite à sa clôture, avec l'attribution question-compétence telle qu'elle
était alors. Recalculer appliquerait l'attribution d'aujourd'hui aux réponses
d'hier et changerait sans le dire une conclusion déjà montrée à un parent.

Par compétence : le dernier mot plutôt qu'une moyenne, combien de tentatives
terminées ont conclu, combien de fois chacun des trois mots, les comptes
cumulés, et une phrase en français construite des mêmes valeurs. Aucun ratio,
aucun pourcentage, aucun score, et un test le vérifie sur la charge utile.

Un bloc `evidence` dit sur quoi la lecture repose : événements reçus, réponses
déclarées, réponses venues du runtime. C'est ce qui fait de cette agrégation une
agrégation « des événements **et** des résultats » et non des seuls résultats.

### La décision qui manquait, et qui est prise

**Un événement du runtime prime sur une réponse déclarée**, quel que soit
l'ordre d'arrivée. Entre deux sources de même nature, la plus récente l'emporte
toujours.

Ce n'est pas une affirmation que l'un serait plus dur à falsifier : les deux
passent par le même navigateur. C'est une question de qui a interprété. Une
réponse `declared` est la conclusion du client ; une réponse `xapi` est le compte
rendu du contenu, relayé tel quel et lu par le serveur. Deux récits d'un même
fait, pas deux faits, et celui que le serveur a lu lui-même est celui qu'il
garde. L'ordre inverse laisserait un client défaire un événement du runtime en
publiant sa propre déclaration juste après.

Les deux lignes restent en base : l'une n'est pas lue, aucune n'est effacée.

## Fichiers créés

- `apps/api/app/models/xapi.py`
- `apps/api/app/xapi/__init__.py`, `statements.py`, `service.py`
- `apps/api/app/schemas/xapi.py`
- `apps/api/app/api/v1/xapi.py`
- `apps/api/app/progress/__init__.py`, `service.py`
- `apps/api/app/schemas/progress.py`
- `apps/api/app/api/v1/progress.py`
- `apps/api/alembic/versions/0010_xapi_statements.py`
- `apps/api/tests/test_xapi_statements.py`, `test_xapi_api.py`,
  `test_progress_api.py`
- `docs/adr/ADR-014-ingestion-xapi.md`
- `docs/backend/evenements-xapi.md`, `docs/backend/progres.md`

## Fichiers modifiés

- `apps/api/app/attempts/service.py` : `_prevailing`, la règle de prééminence
- `apps/api/app/models/attempt.py`, `apps/api/app/schemas/attempt.py` :
  commentaires de `source` mis au présent
- `apps/api/app/models/__init__.py`, `apps/api/app/core/routing.py`
- `apps/api/app/content/page/play.html` : identifiant posé sur chaque événement
- `docs/adr/ADR-012-h5p-standalone-pilote.md` : conditions 6 et 7, conséquences
- `docs/architecture/decision-register.md` : ADR-014, statistiques
- `docs/backend/tentatives-resultats.md`, `docs/backend/runtime-contenu.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, les quatre fiches de l'étape

## Commandes exécutées

Séquence du workflow d'API CI, rejouée dans le conteneur `api` :

```
ruff format --check .
ruff check .
mypy app
alembic upgrade head
alembic check
alembic downgrade base
alembic upgrade head
pytest -q
```

## Tests exécutés

- 58 tests nouveaux : 21 sur la lecture d'un événement hors base, 24 sur l'API
  xAPI, 13 sur les progrès et la prééminence.
- Suite complète rejouée deux fois : une fois sur le schéma courant, une fois
  sur un schéma reconstruit depuis `base`.

## Résultats des tests

```text
Ruff       : vert, format inclus, 119 fichiers
Mypy       : vert sur 66 fichiers
Alembic    : 0010_xapi_statements (head), check vert, downgrade base et retour au head
Pytest     : 499 tests réussis, dont 58 pour l'étape 11
Tests      : un événement sans ticket, avec un ticket inconnu ou avec celui
             d'une autre famille est refusé de la même façon
Tests      : le client ne nomme pas la tentative ; le serveur la déduit du ticket
Tests      : cinq envois du même événement laissent une seule réponse
Tests      : deux événements différents restent deux réponses
Tests      : l'acteur revendiqué n'est conservé nulle part
Tests      : l'URL de lecture ne porte ni enfant, ni pseudonyme, ni code famille
Tests      : les deux horloges restent distinctes
Tests      : un événement du runtime prime, qu'il parle avant ou après
Tests      : un événement de complétion ne termine pas la tentative
Tests      : une tentative non terminée ne compte jamais dans les progrès
Tests      : aucun ratio ni score dans la charge utile des progrès
Tests      : deux lectures des progrès rendent exactement la même chose
Tests      : un parent d'une autre famille reçoit 404, un enfant 403
```

## Critères d'acceptation

- [x] Ingestion et validation des événements xAPI autorisés, avec
      déduplication.
- [x] Acteur pseudonyme posé par le serveur, identité jamais exposée au runtime.
- [x] Agrégation des progrès à partir des événements et des résultats de
      l'étape 10.
- [x] Migration réversible, upgrade, check, downgrade base et retour au head.
- [x] Ruff, Mypy et Pytest verts dans l'ordre du workflow d'API CI.
- [x] Contrôles d'autorisation et d'isolation éprouvés par des tests dédiés.
- [x] ADR-012 condition 6 remplie et son tableau de suivi mis à jour.
- [x] Une seule Pull Request pour toute l'étape.

## Décisions ou ADR

ADR-014, acceptée, qui consigne les cinq décisions prises sans arbitrage
préalable : l'autorisation par le ticket, la déduction de la tentative, le
remplacement de l'acteur, la prééminence du runtime, et l'absence de table
d'agrégats. Chacune est signalée au propriétaire à la clôture.

ADR-012 : condition 6 passée de « à faire » à « remplie », condition 7 complétée
par les deux horloges d'un événement, conséquences mises à jour — plus aucune
condition n'est entièrement à faire.

## Écarts par rapport au prompt

Aucun sur le périmètre. Le web n'a pas été modifié : il reste le prototype de
l'étape 05 et n'appelle pas encore l'API. Brancher le `postMessage` de
`play.html` sur le nouvel endpoint appartient à l'étape 13, où le web parle à
l'API pour la première fois.

## Risques ou dette technique

- **Aucun client n'appelle encore la route.** Elle est éprouvée par ses tests,
  pas par un navigateur réel. C'est le miroir du constat de `PRE-01` — un
  producteur sans destinataire — et il se referme à l'étape 13.
- **Ce n'est pas un LRS.** Pas de `GET` par requête xAPI, pas de `voided`, pas
  de version de spec négociée. C'est écrit dans la documentation pour ne pas
  laisser croire à une conformité que rien ne teste.
- **Le cache local de Ruff appartient à `root`** dans l'arborescence du dépôt,
  probablement laissé par une exécution Docker antérieure. `ruff` lancé
  directement sur la machine échoue à écrire son cache ; il faut `--no-cache`
  ou passer par le conteneur. Sans effet sur la CI. Le venv local est par
  ailleurs incomplet — `argon2-cffi` y manque — donc les contrôles se rejouent
  dans le conteneur `api`, ce qui est aussi ce que fait la CI.
- Faire tourner `SECRET_KEY` change tous les pseudonymes d'acteur. Accepté, et
  écrit dans ADR-014 : le lien à l'enfant est la clé étrangère, pas ce nom.

## Blocages

Aucun.

## Prochaines actions

Étape 12, diagnostic et remédiation. Les progrès de cette étape sont
descriptifs ; nommer une difficulté et proposer une suite est le travail de
l'étape suivante, et c'est délibérément resté hors de celle-ci.

## Mise à jour appliquée à ETAT.md

Section « Étape 11, événements xAPI et progrès, clôturée », résultats techniques,
prochaine action.

## Mise à jour appliquée à PLANNING.md

XAP-01 à XAP-04 passés à « Terminé » avec leurs preuves ; prochaine tâche
pointée sur l'étape 12.
