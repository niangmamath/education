# Modèle identité et famille

## Parent

Le Parent est le compte adulte principal. L’adresse email est unique et sert d’identifiant futur. Le mot de passe est uniquement conservé sous forme hachée.

## Enfant

L’Enfant est un profil restreint rattaché à un Parent. Aucun email et aucun téléphone ne sont stockés. Le pseudonyme est unique et le PIN est uniquement conservé sous forme hachée.

## Relation

`auth_children.parent_id` référence `auth_parents.id`. La suppression d’un Parent supprime ses profils Enfant dans le MVP. Une évolution vers plusieurs responsables par famille nécessitera une nouvelle décision et une table d’association dédiée.

## Unicité et index

L’unicité est toujours déclarée par une `UniqueConstraint` nommée dans `__table_args__`, jamais par `unique=True` sur la colonne. PostgreSQL crée déjà un index unique pour servir cette contrainte, donc aucun index supplémentaire n’est ajouté sur `auth_parents.email` ni sur `auth_children.pseudonym`. Un nom explicite comme `uq_auth_parents_email` remonte dans la `UniqueViolation` renvoyée par le pilote, ce qui permettra aux sous-étapes 06.2 et 06.3 de distinguer les conflits sans analyser un message d’erreur.

Combiner `unique=True` et `index=True` sur une colonne produit un index unique au lieu d’une contrainte : les modèles cessent alors de correspondre à la migration et `alembic check` échoue. Seuls les index qui ne découlent d’aucune contrainte sont déclarés à la main, comme `ix_auth_children_parent_id` sur la clé étrangère.

## Sessions

Aucune table SQL de session n’est créée. ADR-005 impose des identifiants de session opaques stockés dans Redis. Cette implémentation appartient aux sous-étapes 06.2 et 06.3.

## Données sensibles

Les champs `password_hash` et `pin_hash` ne doivent jamais être retournés par l’API. Les données du stage et des démonstrations doivent rester fictives.
