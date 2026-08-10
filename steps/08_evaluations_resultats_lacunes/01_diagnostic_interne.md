# Étape 08.1, créer le moteur d’évaluation interne

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Implémenter un diagnostic simple comme fallback et preuve contrôlée.

## Travaux obligatoires


Créer modèles pour Assessment, Question, Choice, QuestionCompetency, Attempt, Answer et CompetencyResult.

Support MVP : choix unique, choix multiple, vrai/faux et réponse numérique contrôlée.

Ajouter API, services de scoring, migrations et tests.


## Critères d’acceptation


- [ ] Une question peut mesurer plusieurs compétences.
- [ ] Score global et résultats par compétence sont distincts.
- [ ] Historique des tentatives conservé.
- [ ] Correction déterministe testée.


## Livrables

Moteur d’évaluation et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
