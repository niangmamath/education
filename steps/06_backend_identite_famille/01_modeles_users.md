# 06.1, modèles Parent et Élève

## Livrables

- modèles SQLAlchemy 2 `Parent` et `Child` ;
- relation Parent-Enfant avec suppression en cascade ;
- migration Alembic `0002_identity_family_models` ;
- import des modèles dans les métadonnées Alembic ;
- tests statiques des contrats de schéma ;
- documentation du modèle.

## Décisions de périmètre

- une relation directe Parent-Enfant est retenue pour le MVP conformément à ADR-005 ;
- un enfant appartient à un seul parent gestionnaire dans cette première version ;
- le pseudonyme est globalement unique parce qu’il servira d’identifiant de connexion enfant ;
- les mots de passe et PIN ne sont jamais stockés en clair ;
- les sessions ne sont pas stockées en PostgreSQL, elles seront ajoutées dans Redis en 06.2 et 06.3 ;
- aucune donnée d’activité ou de dashboard n’est ajoutée en 06.1.

## Contrôles

- Ruff format et lint ;
- Mypy ;
- Pytest ;
- upgrade Alembic ;
- vérification des tables ;
- downgrade puis upgrade ;
- état final sur la révision 0002.
