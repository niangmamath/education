# Étape 09.4, créer review et publication

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Permettre la validation humaine et la publication versionnée.

## Travaux obligatoires


1. Créer workflow Draft, Processing, Review, Published, Rejected, Archived.
2. Exiger validation pédagogique, licence et mapping compétence.
3. Publier vers préfixe runtime versionné.
4. Empêcher l’écrasement silencieux.
5. Invalider le CDN abstraitement.
6. Journaliser toutes les actions.


## Critères d’acceptation


- [ ] Seul un reviewer publie.
- [ ] Une nouvelle version ne détruit pas l’ancienne.
- [ ] Attribution conservée.
- [ ] Audit disponible.


## Livrables

Workflow de publication et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
