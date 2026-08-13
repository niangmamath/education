# Modèle identité et famille

## Parent

Le Parent est le compte adulte principal. L’adresse email est unique et sert d’identifiant futur. Le mot de passe est uniquement conservé sous forme hachée.

## Enfant

L’Enfant est un profil restreint rattaché à un Parent. Aucun email et aucun téléphone ne sont stockés. Le pseudonyme est unique et le PIN est uniquement conservé sous forme hachée.

## Relation

`auth_children.parent_id` référence `auth_parents.id`. La suppression d’un Parent supprime ses profils Enfant dans le MVP. Une évolution vers plusieurs responsables par famille nécessitera une nouvelle décision et une table d’association dédiée.

## Sessions

Aucune table SQL de session n’est créée. ADR-005 impose des identifiants de session opaques stockés dans Redis. Cette implémentation appartient aux sous-étapes 06.2 et 06.3.

## Données sensibles

Les champs `password_hash` et `pin_hash` ne doivent jamais être retournés par l’API. Les données du stage et des démonstrations doivent rester fictives.
