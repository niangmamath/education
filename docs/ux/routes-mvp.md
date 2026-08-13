# Routes du MVP StudentConnect

## Statuts

- **Publique** : accessible sans session.
- **Parent protégée** : nécessitera une session Parent.
- **Élève protégée** : nécessitera une session Élève.
- **Technique** : réservée au diagnostic.
- **Expérimentale** : hors navigation produit.

## Routes publiques

| Route | Objectif | État actuel | Action principale |
|---|---|---|---|
| `/` | Présenter StudentConnect | Existante, à adapter | Se connecter |
| `/connexion` | Préparer l’accès Parent ou Élève | À créer comme prototype | Continuer |
| `/inscription` | Présenter le futur parcours d’inscription Parent | À créer comme prototype | Commencer |
| `/aide` | Fournir de l’aide et des informations de contact | À créer | Consulter une rubrique |

## Routes Parent protégées futures

| Route | Objectif | Navigation principale | État vide obligatoire |
|---|---|---|---|
| `/parent` | Synthèse familiale | Accueil | Oui |
| `/parent/enfants` | Liste des enfants autorisés | Enfants | Oui |
| `/parent/enfants/[studentId]` | Détail d’un enfant | Depuis Enfants ou Accueil | Oui |
| `/parent/activites` | Activités recommandées et récentes | Activités | Oui |
| `/parent/notifications` | Informations nécessitant une attention | Notifications | Oui |
| `/parent/parametres` | Préférences et aide familiale | Paramètres | Oui |

## Routes Élève protégées futures

| Route | Objectif | Navigation principale | État vide obligatoire |
|---|---|---|---|
| `/eleve` | Accueil et objectif du moment | Accueil | Oui |
| `/eleve/activites` | Choisir ou reprendre une activité | Activités | Oui |
| `/eleve/progression` | Comprendre la progression | Progression | Oui |
| `/eleve/recompenses` | Présenter les récompenses futures sans promesse trompeuse | Récompenses | Oui |

## Routes techniques et expérimentales

| Route | Statut | Règle |
|---|---|---|
| `/health` | Technique existante | Non affichée dans la navigation produit |
| Spike H5P local | Expérimentale | Reste sous `experiments/`, jamais liée depuis le produit |

## Paramètres et identifiants

- `[studentId]` est un identifiant opaque futur.
- Les démonstrations utilisent uniquement des identifiants fictifs.
- Aucun nom, email ou autre donnée personnelle ne doit apparaître dans une URL.
- Une route Parent ne doit jamais accepter un enfant qui n’appartient pas au périmètre autorisé du compte.

## Pages système

- page introuvable avec retour sûr ;
- accès refusé sans révéler l’existence d’une ressource ;
- session expirée avec retour vers `/connexion` ;
- contenu indisponible avec Réessayer et Retour ;
- réseau dégradé avec état de l’action clairement indiqué.
