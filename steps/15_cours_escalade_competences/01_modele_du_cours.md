# 15.1, Modèle du cours

## Objectif

Ajouter le type d'activité `course` à côté de `assessment` et `remediation`,
et le rattacher à la plomberie authored existante, sans nouvelle table.

## Prérequis

- étape précédente clôturée (étape 14) ;
- branche dédiée issue de `main` ;
- dépôt propre ;
- Docker et services requis opérationnels ;
- ADR-013, ADR-017 et ADR-021 relues.

## Livrables

- `app/models/catalog.py` : `ACTIVITY_KIND_COURSE`, ajouté à
  `ACTIVITY_KINDS` et à `AUTHORED_KINDS`.
- Migration Alembic élargissant `ck_catalog_activities_kind` à la nouvelle
  valeur, réversible.
- Tests de contraintes : kind `course` accepté, refusé hors de la liste,
  durée bornée comme les autres activités.

## Hors périmètre

- le service qui donne le cours (15.2) ;
- les routes de lecture et de vérification (15.3) ;
- le contenu pilote (15.4).

## Contrôles

- état Git et diff propres ;
- `alembic check`, downgrade puis retour au head ;
- Ruff, Mypy, Pytest.

## Statut

Terminé.
