# Étape 10.3, projeter les événements

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Mettre à jour session, résultats, gaps et notifications de manière asynchrone.

## Travaux obligatoires


1. Normaliser score, completion, success et durée.
2. Mettre à jour LearningSession.
3. Recalculer CompetencyResult.
4. Réévaluer Gap.
5. Recalculer score académique.
6. Créer notification si règle applicable.
7. Garantir idempotence et reprise.
8. Ajouter monitoring des échecs.


## Critères d’acceptation


- [ ] Rejouer la tâche ne double pas les effets.
- [ ] Échec récupérable.
- [ ] Dashboard peut être invalidé après succès.
- [ ] Traçabilité complète.


## Livrables

Projections et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
