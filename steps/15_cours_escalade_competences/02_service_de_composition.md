# 15.2, Service de composition avec l'examen

## Objectif

Donner automatiquement, sans bloquer l'examen, le cours des compétences que
`app.assessment.tiers.next_sitting` déclare dues — en un seul point d'appel
pour que les cinq sites existants qui donnent déjà l'examen héritent du don
de cours sans être modifiés.

## Prérequis

- 15.1 terminée ;
- `app/assessment/tiers.py` et `app/assessment/service.py` relus.

## Livrables

- `app/course/service.py` :
  - `course_for(db, competency_code)` : activité `course` publiée liée à ce
    code, la plus récente en cas de doublon — même forme que
    `assessment_for`.
  - `give_to(db, child, due)` : assigne, pour chaque code de `due`, le cours
    correspondant s'il existe et si rien n'est déjà ouvert pour lui — même
    garde d'idempotence que `assessment.service.give_to`. Note explicite
    disant que l'examen reste accessible sans avoir fait le cours.
- `app/assessment/service.py:give_to` appelle `course_service.give_to(db,
  child, due)` avec le `due` déjà calculé, en plus de sa propre décision.
- Couvert par les tests d'intégration de 15.4 plutôt que par des tests
  unitaires isolés : `course_for`/`give_to` n'ont de sens qu'exercés contre
  un graphe de prérequis et des affectations réels, comme
  `assessment.tiers.next_sitting` l'était déjà pour l'étape 14.

## Hors périmètre

- les routes HTTP (15.3) ;
- le contenu pilote (15.4) ;
- toute modification de `next_sitting` lui-même.

## Contrôles

- état Git et diff propres ;
- Ruff, Mypy, Pytest ;
- vérifier qu'aucun cycle d'import n'est introduit entre `app.course` et
  `app.assessment`.

## Statut

Terminé.
