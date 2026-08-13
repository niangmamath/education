# Règles de redirection et d’accès

## Portée

Ces règles décrivent le comportement cible. Elles ne constituent pas encore une authentification ou une autorisation implémentée.

## Visiteur non connecté

- peut accéder aux routes publiques ;
- une tentative d’accès Parent ou Élève conduit vers `/connexion` ;
- la cible de retour doit être interne, validée et dépourvue de données sensibles ;
- aucune redirection vers une URL externe fournie par l’utilisateur.

## Session Parent

- accès aux routes Parent autorisées ;
- accès direct aux routes Élève refusé sauf futur mécanisme explicitement conçu ;
- vérification serveur obligatoire de la relation avec chaque enfant ;
- un identifiant invalide ou non autorisé produit une réponse non révélatrice.

## Session Élève

- accès aux routes Élève autorisées ;
- accès aux routes Parent refusé ;
- aucune donnée familiale sensible visible ;
- retour vers l’accueil Élève après connexion.

## Redirection après connexion

Priorité cible :

1. cible interne sûre demandée avant connexion ;
2. accueil correspondant au rôle ;
3. page d’aide si le rôle ou le dossier est incomplet.

## Session expirée

1. interrompre les nouvelles actions protégées ;
2. prévenir l’utilisateur ;
3. conserver uniquement les données non sensibles nécessaires ;
4. rediriger vers `/connexion` ;
5. reprendre sur une cible sûre après reconnexion.

## Accès refusé et ressource absente

- ne pas confirmer qu’un enfant ou une ressource non autorisée existe ;
- utiliser un message générique ;
- journaliser côté serveur sans afficher les détails ;
- proposer une destination sûre.

## Démonstrations de l’étape 05

- aucune route prototype n’est réellement protégée ;
- afficher « Prototype UX, données fictives » ;
- ne pas simuler une authentification réussie comme une sécurité effective ;
- ne pas stocker de rôle de démonstration dans un mécanisme présenté comme sécurisé.

## Critères futurs d’implémentation

- contrôle d’accès côté serveur ;
- tests des matrices rôle-route ;
- prévention des redirections ouvertes ;
- gestion CSRF et session selon l’ADR dédiée ;
- tests de navigation clavier après redirection ;
- pages 401, 403 et 404 cohérentes sans fuite d’information.
