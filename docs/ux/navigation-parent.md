# Navigation de l’espace Parent

## Navigation principale

Ordre proposé :

1. Accueil
2. Enfants
3. Activités
4. Notifications
5. Paramètres

## Bureau

- barre latérale persistante à partir du point de rupture approprié Bootstrap ;
- identité StudentConnect en haut ;
- libellé et icône pour chaque destination ;
- destination active indiquée par texte, forme et couleur ;
- sélecteur d’enfant dans la zone de contenu, pas dans la navigation globale ;
- aide accessible depuis Paramètres et l’en-tête.

## Mobile

- en-tête compact ;
- bouton de menu avec nom accessible ;
- panneau de navigation refermable au clavier ;
- focus replacé sur le bouton d’ouverture après fermeture ;
- destination courante annoncée ;
- aucune action importante accessible uniquement par balayage.

## Fil d’Ariane

Utilisé pour les niveaux profonds :

```text
Accueil > Enfants > Exemple fictif
```

Le sélecteur d’enfant et le fil d’Ariane ont des fonctions distinctes.

## États

### Aucun enfant associé

- masquer les indicateurs vides non utiles ;
- expliquer la situation ;
- proposer l’action future appropriée ;
- conserver l’accès aux paramètres et à l’aide.

### Session expirée

- afficher un message bref ;
- rediriger vers `/connexion` avec une cible de retour sûre ;
- ne pas conserver d’information sensible dans l’URL.

### Accès refusé

- ne pas révéler les données ou l’existence d’un autre enfant ;
- proposer Retour à l’accueil Parent.

## Règles de liens actifs

- `/parent` active uniquement Accueil ;
- `/parent/enfants` et ses sous-routes activent Enfants ;
- les paramètres de requête ne changent pas la destination principale active ;
- un seul élément principal est actif à la fois.
