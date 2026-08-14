# Modèle identité et famille

## Parent

Le Parent est le compte adulte principal. L’adresse email est unique et sert d’identifiant futur. Le mot de passe est uniquement conservé sous forme hachée. Le `family_code`, unique lui aussi, est l’identifiant public par lequel les enfants rejoignent la famille ; il est décrit dans `acces-enfant.md`.

## Enfant

L’Enfant est un profil restreint rattaché à un Parent. Aucun email et aucun téléphone ne sont stockés. Le PIN est uniquement conservé sous forme hachée. Le `status` distingue un profil utilisable, un profil créé par l’enfant et en attente de son parent, et un profil désactivé.

Le pseudonyme est unique **dans la famille** et non sur la plateforme : deux familles peuvent chacune avoir une `lea`, et c’est le code famille qui les distingue à la connexion. Un pseudonyme ne désigne donc jamais un enfant à lui seul.

## Relation

`auth_children.parent_id` référence `auth_parents.id`. La suppression d’un Parent supprime ses profils Enfant dans le MVP. Une évolution vers plusieurs responsables par famille nécessitera une nouvelle décision et une table d’association dédiée.

## Unicité et index

L’unicité est toujours déclarée par une `UniqueConstraint` nommée dans `__table_args__`, jamais par `unique=True` sur la colonne. PostgreSQL crée déjà un index unique pour servir cette contrainte, donc aucun index supplémentaire n’est ajouté sur `auth_parents.email`, sur `auth_parents.family_code` ni sur le couple `auth_children (parent_id, pseudonym)`. Un nom explicite comme `uq_auth_parents_email` remonte dans la `UniqueViolation` renvoyée par le pilote.

L’index composite de `uq_auth_children_parent_pseudonym` commence par `parent_id`, donc il sert déjà les recherches par famille : la clé étrangère n’a pas d’index à elle, et `ix_auth_children_parent_id` a été retiré.

Combiner `unique=True` et `index=True` sur une colonne produit un index unique au lieu d’une contrainte : les modèles cessent alors de correspondre à la migration et `alembic check` échoue. Seuls les index qui ne découlent d’aucune contrainte seraient déclarés à la main ; il n’y en a aucun aujourd’hui.

## Sessions

Aucune table SQL de session n’est créée. ADR-005 impose des identifiants de session opaques stockés dans Redis. Cette implémentation appartient aux sous-étapes 06.2 et 06.3.

## Données sensibles

Les champs `password_hash` et `pin_hash` ne doivent jamais être retournés par l’API. Les données du stage et des démonstrations doivent rester fictives.
