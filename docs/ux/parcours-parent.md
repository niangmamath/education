# Parcours Parent du MVP

## P-01, découvrir puis accéder à StudentConnect

**Entrée :** page publique.

1. Le visiteur découvre la proposition de valeur.
2. Le visiteur choisit Connexion ou Inscription.
3. Le système affiche le formulaire correspondant.
4. Après une future authentification réussie, le parent rejoint son espace.

**Sortie :** espace Parent ou message d’erreur compréhensible.

## P-02, consulter la synthèse familiale

**Entrée :** `/parent`.

1. Le parent identifie l’enfant actuellement sélectionné.
2. Le parent voit la date de dernière mise à jour.
3. Le parent consulte la synthèse de progression.
4. Le parent repère les difficultés prioritaires.
5. Le parent accède à l’activité recommandée ou au détail de l’enfant.

**Sortie :** détail, activité ou aucune action.

## P-03, changer d’enfant

1. Le parent active le sélecteur d’enfant.
2. Le parent choisit un profil autorisé.
3. L’interface annonce le changement.
4. Les informations visibles sont remplacées.

**Cas limite :** un seul enfant, aucun enfant associé, accès refusé.

## P-04, consulter le détail d’un enfant

**Entrée :** `/parent/enfants/[studentId]` avec identifiant fictif dans les démonstrations.

1. Vérifier l’enfant sélectionné.
2. Consulter progression, compétences et difficultés.
3. Ouvrir une recommandation.
4. Revenir à la synthèse sans perdre le contexte.

## P-05, gérer une absence de données

1. Afficher un état vide explicatif.
2. Expliquer pourquoi aucune donnée n’est disponible.
3. Proposer une action réelle et sûre.
4. Ne jamais afficher un score synthétique fictif comme s’il était calculé.

## P-06, gérer une erreur ou une session expirée

1. Afficher un message sans détail technique.
2. Préserver les informations non sensibles déjà saisies si possible.
3. Proposer Réessayer ou Se reconnecter.
4. Fournir un accès à l’aide.

## Règles UX

- données de démonstration marquées « Exemple fictif » ;
- score académique présenté comme emplacement futur tant que le calcul n’existe pas ;
- priorité aux prochaines actions plutôt qu’aux graphiques décoratifs ;
- navigation clavier complète ;
- retour arrière prévisible.
