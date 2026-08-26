# Rapport de clôture, étape 15, cours d'escalade de compétences

## Métadonnées

- Étape : 15, cours d'escalade de compétences
- Sous-étape : 15.1 à 15.5 (étape entière)
- Date/heure : 26 août 2026, ~16h00
- Agent : Claude Sonnet 5
- ID planning : COU-01 à COU-05 (à créer dans PLANNING.md)
- Branche : `feat/etape-15-cours-escalade`
- Commit/PR : voir historique de clôture ci-dessous
- Statut : Terminé

## Objectif

Construire la brique qui **enseigne** : un enfant ayant maîtrisé les
compétences d'un palier reçoit, en même temps que l'examen du palier
suivant, un cours natif portant sur ce palier — pour qu'elle puisse
apprendre sur la plateforme plutôt que de supposer qu'elle l'a appris
ailleurs, hypothèse sur laquelle reposaient jusqu'ici l'examen et les fiches
de remédiation.

## Prérequis vérifiés

- Étape 14 clôturée, HORS-13 et HORS-14 terminés.
- Branche dédiée issue de `main`, dépôt propre au démarrage.
- Docker Compose (`docker-compose.dev.yml`) opérationnel : postgres, redis,
  storage, api.
- ADR-013, ADR-017, ADR-021 relues.

## Décisions soumises et tranchées par le propriétaire avant construction

Même démarche qu'à l'ouverture des étapes 07, 08 et 14 : recherche du code
existant, plan soumis, décisions structurantes posées avant d'écrire le
premier fichier.

1. **Don automatique, non bloquant.** Le cours est donné par la plateforme
   dès qu'un palier est prêt, comme l'examen, mais l'examen reste
   accessible sans être passé par le cours.
2. **Leçon native avec vérification à la volée, sans conséquence sur la
   maîtrise.** Une leçon écrite ici, comme les fiches, suivie de quelques
   questions expliquées qui ne produisent aucune lecture de compétence.

## Travaux réalisés

### 15.1, modèle du cours

`ACTIVITY_KIND_COURSE` ajouté à `ACTIVITY_KINDS` et `AUTHORED_KINDS`
(`apps/api/app/models/catalog.py`). Migration `0017_course_kind`,
réversible, élargit `ck_catalog_activities_kind` à `course`. Aucune
nouvelle table : un cours réutilise `catalog_activities`,
`catalog_activity_competencies` et `authored_questions`.

### 15.2, service de composition

`app/course/service.py`, nouveau : `course_for(db, competency_code)` et
`give_to(db, child, due)`. `app/assessment/service.py:give_to` calcule
`due` une seule fois et le partage avec `course_service.give_to`, un seul
point d'appel touché — les cinq sites existants qui donnent déjà l'examen
héritent du don de cours sans modification.

### 15.3, API du cours

`app/api/v1/cours.py`, nouveau, deux routes sur le modèle de `fiches.py` :
lecture (`GET /me/activities/{id}/cours`) et vérification
(`POST /me/cours/{id}/answers`), cette dernière **sans jamais passer par un
`Attempt`**. `app.authored.service.grade` prend désormais un
`assignment_id` plutôt qu'une `Attempt`, dont elle n'utilisait que ce
champ ; ses trois appelants (fiches, examen, script de démonstration) mis à
jour, comportement inchangé pour eux. `open_sheet_for` renommée
`open_authored_activity_for`, servant désormais deux natures.

### 15.4, boucle de bout en bout et contenu pilote

Deux cours natifs pilotes (`ci-fr-lettres`, `ci-ma-denombrer`,
`app/demo/cours.py`), sur des compétences déjà couvertes par une fiche.
`tests/test_course_tiers.py`, six tests d'intégration contre PostgreSQL
réel et l'API complète. Boucle vérifiée en direct sur la pile Docker de ce
worktree : cours et examen donnés ensemble à l'enfant de démonstration
`noa` (classe CI), lecture, réponse et achèvement du cours sans effet sur
`GET /api/v1/me/progress`.

### 15.5, documentation et clôture

ADR-022 écrite. `docs/backend/cours-escalade.md` créé ;
`examen-initiation.md`, `fiches-remediation.md` et
`diagnostic-remediation.md` référencent la nouvelle brique.
`docs/architecture/decision-register.md` mis à jour (23 ADR). `ETAT.md`,
`PLANNING.md` et `steps/MANIFESTE.md` mis à jour.

## Deux défauts trouvés par la suite de tests complète, corrigés

1. **`quick_repairs` restreint à tort au seul type `remediation`.** Une
   première version du filtre anti-collision (voir ci-dessous) excluait
   tout ce qui n'était pas `remediation`, alors que `quick_repairs` a
   toujours eu vocation à proposer une réparation en H5P ou PhET, pas
   seulement une fiche native — `test_diagnostic_api.py` l'a montré
   immédiatement. Corrigé en excluant seulement `assessment` et `course`
   (`Activity.kind.not_in(_NOT_A_REPAIR)`), laissant tout le reste passer
   comme avant.
2. **`GET /catalog/kinds` et le filtre de `GET /catalog/activities`
   n'excluaient que `assessment`.** Un cours, donné automatiquement comme
   l'examen et jamais parcouru par un parent, rejoint l'exclusion
   (`_NOT_BROWSABLE`, `app/api/v1/catalog.py`) —
   `test_catalog_api.py::test_the_kinds_are_served_so_a_client_need_not_hard_code_them`
   l'a révélé.

Les deux venaient du même risque, anticipé mais mal réglé du premier coup :
un cours partage la plomberie authorée et la table du catalogue avec des
activités qui, elles, doivent rester joignables autrement.

## Fichiers créés

- `apps/api/app/course/__init__.py`, `apps/api/app/course/service.py`
- `apps/api/app/api/v1/cours.py`
- `apps/api/app/demo/cours.py`
- `apps/api/alembic/versions/0017_course_kind.py`
- `apps/api/tests/test_course_tiers.py`
- `docs/adr/ADR-022-cours-donne-non-bloquant.md`
- `docs/backend/cours-escalade.md`
- `steps/15_cours_escalade_competences/` (cinq fiches, README réécrit)

## Fichiers modifiés

- `apps/api/app/models/catalog.py`, `apps/api/app/assessment/service.py`
- `apps/api/app/authored/service.py`, `apps/api/app/api/v1/fiches.py`
- `apps/api/app/api/v1/assessment.py`, `apps/api/app/api/v1/catalog.py`
- `apps/api/app/core/routing.py`, `apps/api/app/diagnostic/remediation.py`
- `apps/api/app/schemas/authored.py`, `apps/api/app/demo/__main__.py`
- `apps/api/tests/test_catalog_models.py`
- `docs/backend/examen-initiation.md`, `fiches-remediation.md`,
  `diagnostic-remediation.md`, `docs/architecture/decision-register.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, `steps/MANIFESTE.md`

## Commandes exécutées

```text
ruff format --check .
ruff check .
mypy app
alembic upgrade head && alembic check
pytest -q
```

## Résultats des tests

```text
Ruff       : vert, format inclus
Mypy       : vert sur 96 fichiers
Alembic    : 0017_course_kind (head), réversible, aucune dérive détectée
Pytest     : 2552 tests réussis, 7 nouveaux (1 contrainte, 6 test_course_tiers.py)
API vivante: enfant de démonstration CI, cours et examen donnés ensemble,
             lecture-réponse-achèvement du cours sans effet sur /me/progress
```

Deux tests préexistants de `test_health.py::TestCORS` échouent, sans lien
avec cette étape : ils supposent l'origine `http://localhost:3000`, ce
worktree isolé servant sur le port `3100` (`.env`). Signalé depuis l'étape
14, non corrigé — hors périmètre.

## Critères d'acceptation

- [x] Un cours est donné automatiquement, à la même lecture que l'examen
      du palier qu'il précède.
- [x] L'examen reste accessible sans avoir ouvert le cours.
- [x] Répondre à une question du cours, ou l'achever, ne modifie aucune
      lecture de compétence.
- [x] Un cours ne réapparaît pas une fois sa compétence testée.
- [x] Deux cours pilotes réels, la boucle complète démontrable de bout en
      bout.
- [x] Ruff, Mypy, Alembic et Pytest verts.

## Décisions ou ADR

- **ADR-022**, le cours est donné automatiquement, jamais une porte.
  Décisions confirmées par le propriétaire le 26 août 2026, avant
  construction.

## Écarts par rapport au plan

Aucun sur le fond. Deux corrections supplémentaires, non prévues par le
plan initial, ont été ajoutées en cours de route après que la suite de
tests complète les a révélées (voir « Deux défauts trouvés » ci-dessus).

## Risques ou dette technique

- Deux cours pilotes seulement sur cinquante-quatre compétences. Couvrir le
  reste est une dette assumée, à traiter hors étape comme HORS-04 puis
  HORS-09 l'ont fait pour les fiches.
- Les deux tests CORS de `test_health.py` restent rouges dans ce worktree,
  pour une raison déjà comprise et sans rapport avec cette étape.

## Blocages

Aucun.

## Prochaines actions

Étapes 16 à 18 (notifications, sécurité et exploitation, validation et
livraison du MVP) restent en brouillon.

## Mise à jour appliquée à ETAT.md

Section « Étape 15, cours d'escalade de compétences, clôturée » ajoutée.
« Prochaine action » pointe vers l'étape 16.

## Mise à jour appliquée à PLANNING.md

Nouvelle Phase 11 (COU-01 à COU-05) ajoutée, passée à Terminé. « Prochaine
tâche » mise à jour.
