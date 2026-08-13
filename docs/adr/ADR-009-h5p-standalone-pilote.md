# ADR-009, H5P Standalone pour le pilote

- Statut : Accepté sous conditions
- Date : 13 août 2026

## Décision

Utiliser `h5p-standalone` comme base du lecteur H5P du pilote StudentConnect avec `H5P.TrueFalse 1.8` comme seul type actuellement autorisé. Tout autre type est refusé par défaut jusqu’à un test et une décision explicites.

## Conditions

1. Paquets privés avant validation.
2. Quarantaine, extraction sécurisée, limites, contrôle MIME et antivirus.
3. Bibliothèques préparées hors ligne, contrôlées et figées comme artefacts internes.
4. Aucun CLI H5P dans le chemin de production.
5. Runtime isolé par iframe et origine dédiée avec CSP restrictive.
6. Endpoint xAPI authentifié et autorisé.
7. Date de réception serveur distincte du timestamp source.
8. Licence et provenance vérifiées avant publication.

## Preuves

- Paquet : `true-false-question-34806.h5p`
- SHA-256 : `9914c27552f00aa91d4a29e85f6a299b11f984030c3451658fb0246f84b07f3c`
- Rendu et interaction : réussis
- Score : `1/1`
- xAPI : `answered`, succès et complétion à `true`

## Conséquences

Le MVP peut avancer sans serveur H5P complet, mais la production exige encore le pipeline d’import, l’isolation, la publication contrôlée et l’endpoint xAPI.
