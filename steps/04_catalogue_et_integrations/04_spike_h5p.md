# Prompt 04.4, réaliser le POC H5P

Étudier l’option retenue dans ADR-004.

## Objectif

Faire exécuter une activité H5P et enregistrer au minimum : tentative, score, score maximal et complétion.

## Contraintes

- même origine ou intégration compatible pour écouter xAPI ;
- déduplication des événements ;
- validation serveur ;
- aucune confiance absolue dans le navigateur ;
- fallback vers un quiz Django si le POC bloque le projet.

## Livrables

- POC fonctionnel ou rapport de blocage précis ;
- endpoint documenté ;
- tests ;
- rapport de réalisation.
