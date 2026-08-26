# 14.5, Documentation et clôture

## Objectif

Faire correspondre la documentation au nouveau service par palier, consigner
la décision de portée dans une ADR, et clôturer l'étape.

## Prérequis

- 14.1 à 14.4 clôturées ;
- branche dédiée issue de `main` ;
- dépôt propre.

## Livrables

- `docs/backend/examen-initiation.md`, `docs/backend/classes-et-passage.md`
  et `docs/backend/diagnostic-remediation.md` réécrits pour décrire le
  service par palier.
- Nouvelle ADR consignant : le palier reste borné à la classe déclarée, la
  descente vers une classe antérieure reste réactive (déclenchée par un
  échec), et le seuil de maîtrise hérité (`RULE_ALL_CORRECT`) sans nouveau
  seuil inventé. Registre des décisions mis à jour.
- Séquence complète de l'API CI rejouée en local : Ruff, Mypy, `alembic
  check`, Pytest.
- Rapport de clôture au format `MODELE_RAPPORT.md`.
- `ETAT.md` et `PLANNING.md` mis à jour.
- Une seule Pull Request pour toute l'étape 14, fusion vers `main` une fois
  tout vert.
- `steps/MANIFESTE.md` régénéré.

## Hors périmètre

- toute fonctionnalité de l'étape 15 (cours d'escalade de compétences).

## Contrôles

- état Git et diff propres ;
- Ruff, Mypy, `alembic check` et Pytest verts ;
- CI distante réussie sur la Pull Request puis sur `main` ;
- ETAT et PLANNING mis à jour après preuves.

## Statut

À faire.
