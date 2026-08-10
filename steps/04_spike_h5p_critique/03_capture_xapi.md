# Étape 04.3, valider la capture xAPI

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Capturer un événement H5P et le transférer de manière contrôlée.

## Travaux obligatoires


1. Écouter le dispatcher xAPI H5P.
2. Filtrer les événements attendus.
3. Ajouter un identifiant de session de test.
4. Si iframe, utiliser `postMessage` avec validation d’origine.
5. Envoyer vers un endpoint FastAPI de spike.
6. Dédupliquer par event_id.
7. Stocker le statement brut de test en JSONB ou mémoire selon l’état de la base.
8. Documenter les événements réellement émis par chaque type.


## Critères d’acceptation


- [ ] Au moins un événement réel est capturé.
- [ ] L’origine est vérifiée.
- [ ] Un doublon est rejeté ou ignoré idempotemment.
- [ ] Les limites xAPI sont documentées.


## Livrables

POC bout en bout et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
