# Étape 09.3, créer le pipeline H5P sécurisé

## Prérequis

Lire les fichiers racine et le dernier rapport disponible.

## Objectif

Valider et extraire les paquets H5P en tâche Celery.

## Travaux obligatoires


1. Télécharger depuis quarantaine.
2. Vérifier checksum, taille et signature ZIP.
3. Bloquer path traversal.
4. Limiter nombre de fichiers, profondeur et taille extraite.
5. Détecter archives imbriquées et ZIP bombs.
6. Analyser antivirus si disponible, sinon documenter le contrôle manquant.
7. Lire manifests H5P.
8. Vérifier allowlist de bibliothèques.
9. Extraire dans un préfixe versionné non public.
10. Produire rapport de validation machine.


## Critères d’acceptation


- [ ] Paquet valide traité.
- [ ] ZIP bomb et path traversal rejetés en test.
- [ ] Worker idempotent.
- [ ] Aucun fichier publié avant review.


## Livrables

Pipeline Celery, tests de sécurité et rapport.

## Clôture obligatoire

- Exécuter les tests pertinents.
- Créer un rapport selon `MODELE_RAPPORT.md` dans ce dossier.
- Mettre à jour `ETAT.md`.
- Mettre à jour la ligne correspondante de `PLANNING.md`.
- Ne pas passer à la sous-étape suivante si le statut est `Bloqué`.
