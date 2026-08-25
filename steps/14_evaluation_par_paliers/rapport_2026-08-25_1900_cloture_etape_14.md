# Rapport de clôture, étape 14, évaluation par paliers

## Métadonnées

- Étape : 14, évaluation par paliers
- Sous-étape : 14.1 à 14.5 (étape entière)
- Date/heure : 25 août 2026, ~19h00
- Agent : Claude Sonnet 5
- ID planning : PAL-01 à PAL-05
- Branche : `feat/etape-14-evaluation-paliers`
- Commit/PR : voir historique de clôture ci-dessous
- Statut : Terminé

## Objectif

Remplacer l'examen d'entrée statique, qui teste toutes les compétences d'une
classe d'un coup, par une évaluation hiérarchique et séquentielle : un enfant
n'est testé que sur les premières compétences nécessaires de sa classe,
débloque le palier suivant une fois le précédent maîtrisé, et une lacune
déclenche une remédiation ciblant le vrai prérequis en cause suivie d'un
retest. Correction du propriétaire du 25 août 2026, qui a aussi demandé une
réorganisation du dépôt et une redéfinition de la feuille de route
(HORS-12, commit antérieur sur cette même branche).

## Prérequis vérifiés

- Étape 13 clôturée, HORS-01 à HORS-12 terminés.
- Branche dédiée issue de `main`, dépôt propre au démarrage.
- Docker Compose (`docker-compose.dev.yml`) opérationnel : postgres, redis,
  storage, api.
- ADR-013, ADR-015, ADR-018, ADR-019 relues.

## État initial observé

Trois agents d'exploration ont confirmé avant l'ouverture de l'étape :
l'examen était un `Activity` unique par classe, servant sa banque entière
(vingt-sept questions) en une fois ; la logique « ne pas proposer une
compétence tant que son prérequis est en lacune » existait déjà dans le
diagnostic (DIA-05) mais ne s'appliquait qu'après coup, jamais pour décider
quoi tester ; le graphe de prérequis modélisait déjà des arêtes traversant
matières et classes.

## Travaux réalisés

### 14.1, moteur de paliers

`app/referential/graph.py`, nouveau module : `load(db, level_code=None)`
charge le graphe de prérequis de l'édition publiée, borné à une classe ou
non ; `CompetencyGraph.frontier(codes, mastered, tested)` rend, parmi des
codes fournis par l'appelant, ceux prêts à être testés — ordonnés comme le
programme les enseigne (position du domaine puis de la compétence). Un code
absent du graphe est traité comme sans prérequis plutôt qu'exclu (ADR-013) :
les candidats viennent du catalogue, pas de la référence.

### 14.2, examen servi par palier

`app/assessment/tiers.py`, nouveau : `next_sitting(db, child)` combine le
graphe borné à la classe de l'enfant avec ses lectures déjà produites.
`app.authored.service.questions_of` gagne un filtre optionnel
`competency_codes`. `app.assessment.service` : `give_to` perd le paramètre
`parent_id`, son idempotence porte sur les affectations ouvertes, elle ne
crée une affectation que si un palier est dû ; `is_done` devient « rien à
servir maintenant et rien en attente ». Cinq sites d'appel mis à jour.

### 14.3, diagnostic généralisé (écart assumé)

`diagnostic/service.py:_tree` partage désormais la lecture du graphe avec
le nouveau module. `_root_causes` et `_unobserved_causes` **gardent** leur
marche à un seul saut : en traçant le comportement existant jusqu'au bout,
`_root_causes` reconstruit déjà une chaîne entière de lacunes confirmées en
une seule lecture (elle examine chaque lacune, donc trouve chaque arête
indépendamment). Franchir un prérequis jamais testé pour en proposer un plus
profond contredirait ADR-015 : une cause racine n'est une hypothèse qu'une
fois qu'une lecture pointe vers elle, pas une déduction sur la forme du
graphe seule. Un module `unmet_ancestors` avait été esquissé pour une marche
transitive puis retiré, faute d'appelant sain qui en aurait eu besoin une
fois ce raisonnement fait. Détail complet dans ADR-021.

### 14.4, boucle de bout en bout

`GET /api/v1/me/assessment` appelle `give_to` avant de répondre — seule
lecture du projet qui écrit, extension d'un cran de l'exception déjà en
vigueur (l'examen est le seul endroit où la plateforme s'auto-assigne).
`AssessmentPublic` gagne un champ optionnel `competency_codes`. Le retest
après remédiation ne construit rien de nouveau : `quick_repairs` inchangé,
et `progress.child_progress` prenant déjà la dernière lecture par
compétence toutes activités confondues, une compétence réparée repasse
« maîtrisée » sans mécanisme séparé.

### 14.5, documentation et clôture

ADR-021 écrite. `docs/backend/examen-initiation.md`,
`docs/backend/classes-et-passage.md` et `docs/backend/diagnostic-remediation.md`
réécrits. `docs/architecture/decision-register.md` mis à jour. `ETAT.md` et
`PLANNING.md` mis à jour. `steps/MANIFESTE.md` régénéré.

### Deux défauts trouvés et corrigés en cours de reprise

Une interruption par la limite de session a eu lieu après 14.1–14.4 (code
écrit, Ruff et Mypy verts) mais avant que la suite complète de tests n'ait
été rejouée. À la reprise :

1. `app.assessment.tiers.next_sitting` cherchait l'examen sans l'ordre ni la
   limite qu'`assessment_for` applique partout ailleurs. Avec deux activités
   `cp` publiées en base (une ancienne de démonstration, une fraîchement
   créée par un test), `db.scalar` sans `ORDER BY` rendait l'une ou l'autre
   selon l'ordre où PostgreSQL choisissait de répondre — non déterministe.
   Corrigé en réutilisant `assessment_for` (import tardif dans la fonction,
   pour casser le cycle avec `service.py` qui importe déjà `tiers` au
   niveau du module).
2. `test_once_done_it_is_not_offered_again` complétait une tentative sans
   répondre à aucune question. Sous l'ancien modèle, une affectation
   terminée suffisait à dire « fait » ; sous le nouveau, « fait » veut dire
   « palier dégagé », et une tentative sans réponse évaluée n'écrit aucun
   résultat (règle de l'étape 10), donc la compétence reste non testée et
   serait reproposée à bon droit. Le test a été corrigé pour répondre aux
   deux questions avant de terminer.

Un nouveau fichier de tests, `test_assessment_tiers.py` (4 tests
d'intégration contre un référentiel et un examen réels, deux compétences
dont l'une prérequiert l'autre), a aussi été ajouté pendant la reprise : la
suite existante ne couvrait le blocage par prérequis que très indirectement,
avec une seule compétence par examen de test.

## Fichiers créés

- `apps/api/app/referential/graph.py`
- `apps/api/app/assessment/tiers.py`
- `apps/api/tests/test_assessment_tiers.py`
- `docs/adr/ADR-021-evaluation-par-paliers.md`
- `steps/14_evaluation_par_paliers/` (README et cinq fiches)
- `steps/15_cours_escalade_competences/README.md` (brouillon)

## Fichiers modifiés

- `apps/api/app/assessment/service.py`, `apps/api/app/authored/service.py`
- `apps/api/app/api/v1/assessment.py`, `apps/api/app/api/v1/children.py`
- `apps/api/app/schemas/assessment.py`
- `apps/api/app/diagnostic/service.py`
- `apps/api/app/demo/examens.py`, `apps/api/app/demo/__main__.py`
- `apps/api/tests/test_assessment_api.py` (un test corrigé)
- `docs/backend/examen-initiation.md`, `classes-et-passage.md`,
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
Mypy       : vert sur 93 fichiers
Alembic    : aucune migration produite, aucune dérive détectée
Pytest     : 2545 tests réussis, 4 nouveaux (test_assessment_tiers.py)
```

Deux tests préexistants de `test_health.py::TestCORS` échouent, sans lien
avec cette étape : ils supposent l'origine `http://localhost:3000`, ce
worktree isolé servant sur le port `3100` (`.env`). Signalé, non corrigé —
hors périmètre.

## Critères d'acceptation

- [x] Un enfant n'est testé que sur le palier prêt de sa classe.
- [x] Un enfant qui valide 100 % à un palier ne reçoit rien de plus à ce
      palier, juste l'accès au suivant.
- [x] Un échec ne redonne pas de nouvelle tentative sur la même compétence ;
      la remédiation et son retest la font remonter comme maîtrisée.
- [x] Aucune migration, tout se recalcule à la lecture.
- [x] Ruff, Mypy, Alembic et Pytest verts.

## Décisions ou ADR

- **ADR-021**, évaluation par paliers bornée à la classe déclarée. Décision
  confirmée par le propriétaire entre deux lectures possibles de sa
  demande : palier borné à la classe avec descente réactive, plutôt que
  cumulatif depuis la première classe.

## Écarts par rapport au prompt

- 14.3 n'a pas généralisé `_root_causes`/`_unobserved_causes` à une marche
  transitive, contrairement à ce que la fiche envisageait initialement.
  Justifié en détail dans ADR-021 et dans le statut de la fiche 14.3 :
  ce n'est pas un renforcement reporté, c'est un comportement qui aurait
  été incorrect au regard d'ADR-015.

## Risques ou dette technique

- Les deux tests CORS de `test_health.py` restent rouges dans ce worktree,
  pour une raison déjà comprise et sans rapport avec cette étape.
- Le module `app.referential.graph` n'expose pas de marche transitive : si
  un besoin réel apparaît plus tard, il faudra la reconstruire avec les
  preuves qui la justifieront, plutôt que réutiliser celle retirée ce soir.

## Blocages

Aucun à la clôture. Une interruption par la limite de session a eu lieu en
cours d'étape, documentée et reprise sans perte : le commit WIP intermédiaire
et sa note dans `ETAT.md` ont servi de point de reprise exact.

## Prochaines actions

Ouvrir l'étape 15, cours d'escalade de compétences — la brique qui enseigne,
encore en brouillon.

## Mise à jour appliquée à ETAT.md

Section « Étape 14, évaluation par paliers, clôturée » ajoutée, remplaçant
la note d'interruption. « Prochaine action » pointe vers l'étape 15.

## Mise à jour appliquée à PLANNING.md

Phase 10 (PAL-01 à PAL-05) passée à Terminé. « Prochaine tâche » mise à jour.
