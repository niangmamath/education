# Matrice besoins et écrans

## Légende

- **Public** : accessible sans future authentification.
- **Parent protégé** : nécessitera une session Parent.
- **Élève protégé** : nécessitera une session Élève.
- **Démonstration** : données fictives explicitement signalées.

| Besoin | Public | Écran ou route cible | Priorité | État vide requis | Données réelles disponibles |
|---|---|---|---|---|---|
| Comprendre StudentConnect | Visiteur | `/` | Haute | Non | Contenu éditorial |
| Se connecter | Visiteur | `/connexion` | Haute | Non | Non implémenté |
| Créer un accès | Visiteur | `/inscription` | Haute | Non | Non implémenté |
| Obtenir de l’aide | Tous | `/aide` | Moyenne | Non | Contenu éditorial |
| Voir la synthèse familiale | Parent protégé | `/parent` | Haute | Oui | Non implémenté |
| Lister les enfants | Parent protégé | `/parent/enfants` | Haute | Oui | Non implémenté |
| Consulter un enfant | Parent protégé | `/parent/enfants/[studentId]` | Haute | Oui | Non implémenté |
| Voir les activités | Parent protégé | `/parent/activites` | Moyenne | Oui | Non implémenté |
| Voir les notifications | Parent protégé | `/parent/notifications` | Moyenne | Oui | Non implémenté |
| Gérer les paramètres | Parent protégé | `/parent/parametres` | Moyenne | Oui | Non implémenté |
| Voir l’objectif du moment | Élève protégé | `/eleve` | Haute | Oui | Non implémenté |
| Choisir une activité | Élève protégé | `/eleve/activites` | Haute | Oui | Non implémenté |
| Voir la progression | Élève protégé | `/eleve/progression` | Haute | Oui | Non implémenté |
| Voir les récompenses futures | Élève protégé | `/eleve/recompenses` | Basse | Oui | Non implémenté |
| Vérifier le frontend | Technique | `/health` | Haute | Non | Déjà disponible |

## États obligatoires par écran métier

Chaque écran métier futur doit prévoir : chargement, vide, erreur, succès, accès refusé, connexion requise, contenu indisponible et réseau dégradé.

## Données de démonstration

Les maquettes et écrans de l’étape 05 peuvent utiliser des données fictives, avec un libellé visible « Exemple fictif ». Aucun score ou résultat fictif ne doit être présenté comme calculé par le système.
