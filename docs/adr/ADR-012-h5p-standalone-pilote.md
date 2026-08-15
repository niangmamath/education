# ADR-012, H5P Standalone pour le pilote

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

## Suivi des conditions

Une ADR acceptée sous conditions sans suivi de ses conditions n’est plus qu’une
ADR acceptée. État au 15 août 2026.

| # | Condition | État | Où |
|---|---|---|---|
| 1 | Paquets privés avant validation | Remplie | Buckets privés depuis l’étape 03 ; aucune réponse n’expose de clé d’objet (08.3) |
| 2 | Quarantaine, extraction sécurisée, limites, MIME et antivirus | **Partielle** | 08.2 lit l’archive sans jamais l’extraire, refuse chemins remontants et absolus, plus de 500 entrées, les bombes de décompression et les fichiers de plus de 20 Mo. **Aucun antivirus**, faute de scanner dans l’environnement de stage |
| 3 | Bibliothèques figées comme artefacts internes | Remplie | Déploiement `PRE-01`, avec inventaire des empreintes : un artefact que personne ne peut nommer n’est pas figé |
| 4 | Aucun CLI H5P dans le chemin de production | Remplie | Ni éditeur ni CLI ; l’enregistrement est une commande du projet (08.2) |
| 5 | Runtime isolé par iframe et origine dédiée à CSP restrictive | Remplie | Origine `content` servie par nginx, `PRE-01` |
| 6 | Endpoint xAPI authentifié et autorisé | **À faire** | Étape 11. `play.html` remonte déjà les événements par `postMessage`, sans destinataire côté serveur |
| 7 | Date de réception serveur distincte du timestamp source | Remplie | `attempt_responses.recorded_at`, horloge du serveur (10.1) |
| 8 | Licence et provenance vérifiées avant publication | **Partielle** | Les champs existent et ne sortent jamais par HTTP ; rien ne les vérifie automatiquement |

## Conséquences

Le MVP peut avancer sans serveur H5P complet. Restent dus avant une mise en
production : l’antivirus de la condition 2, l’endpoint xAPI de la condition 6, et
la vérification de licence de la condition 8.
