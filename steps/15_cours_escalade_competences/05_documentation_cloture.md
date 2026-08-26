# 15.5, Documentation et clôture

## Objectif

Consigner les décisions, mettre à jour la documentation et clôturer l'étape
par une seule Pull Request.

## Prérequis

- 15.1 à 15.4 terminées.

## Livrables

- ADR-022 : don automatique non bloquant, leçon native avec vérification
  sans conséquence sur la maîtrise, choix de ne pas faire transiter les
  vérifications par `attempts`.
- Nouveau document `docs/backend/cours-escalade.md`, registre des décisions
  mis à jour, `steps/MANIFESTE.md` régénéré.
- Séquence complète de l'API CI rejouée en local (Ruff, Mypy, Alembic check
  et cycle downgrade/upgrade, Pytest).
- Rapport de clôture, `ETAT.md` et `PLANNING.md` mis à jour.

## Hors périmètre

- toute nouvelle fonctionnalité non déjà livrée par 15.1 à 15.4.

## Contrôles

- état Git et diff propres ;
- commit et push ;
- CI distante réussie ;
- fusion contrôlée vers `main`.

## Statut

Terminé.
