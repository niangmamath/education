# ADR-012, H5P Standalone pour le pilote

- Statut : Accepté sous conditions
- Date : 13 août 2026, **amendée le 17 août 2026**

## Décision

Utiliser `h5p-standalone` comme base du lecteur H5P du pilote StudentConnect. Tout type non listé est refusé par défaut jusqu’à un test et une décision explicites.

## Amendement du 17 août 2026, huit types au lieu d’un

Le pilote n’autorisait que `H5P.TrueFalse 1.8`. **Un seul type ne peut pas porter une matière** : une dictée doit s’entendre, un rangement doit se manipuler, et une question vrai-ou-faux n’exprime ni l’un ni l’autre. Le propriétaire a amendé la décision et validé la liste.

| Type | Ce qu’il apporte que les autres n’ont pas |
|---|---|
| `H5P.Dictation` | **Le son.** C’est le seul qui paie une dette réelle : tout le reste, la plateforme sait déjà le demander dans une fiche qu’elle a écrite |
| `H5P.DragText` | Remettre en ordre |
| `H5P.DragQuestion` | Le geste sur une image |
| `H5P.MarkTheWords` | Repérer dans un texte |
| `H5P.Blanks` | Le texte à trous |
| `H5P.MultiChoice` | Le QCM avec image |
| `H5P.SingleChoiceSet` | Une suite de choix uniques |
| `H5P.TrueFalse` | Vrai ou faux, déjà en place |

**Trois refus argumentés**, pour qu’ils ne soient pas repris par inadvertance :

- `H5P.QuestionSet` regroupe plusieurs questions sous une activité. Rattacher chacune à sa compétence demande de lire les identifiants de sous-contenu dans l’archive. C’est faisable et ce n’est pas gratuit ;
- `H5P.ArithmeticQuiz` chronomètre l’enfant, ce que cette plateforme ne fait pas ;
- `H5P.InteractiveVideo`, `H5P.Column`, `H5P.Accordion` sont des conteneurs et ne produisent aucune lecture.

**La version cesse d’être figée dans le code**, et c’est un relâchement délibéré. Le gel est assuré par le `sha256`, qui dit « voici les octets qui ont été vérifiés » — ce qu’une chaîne de version ne dit pas, puisque deux compilations d’une même version ne sont pas le même fichier. Épingler la version ne refusait jamais qu’un paquet trop récent pour une constante que personne n’avait pensé à relever.

La contrainte de vérification en base reste une contrainte : ajouter un type coûte toujours une migration et un amendement, et rien ne peut entrer dans le catalogue par une simple modification applicative. C’est `0015_h5p_allowed_libraries`.

**La condition 3 change de sens sans changer d’exigence.** « Bibliothèques préparées hors ligne » se lisait comme un travail manuel ; il s’avère qu’un `.h5p` complet porte déjà ses bibliothèques, et `python -m app.catalog libraries` les en extrait sans rien télécharger. Une bibliothèque déjà présente n’est jamais écrasée : c’est celle qui a été vérifiée avec le premier paquet, et la remplacer changerait ce que joue un contenu déjà déployé sans changer son empreinte.

Un piège est consigné parce qu’il coûte une soirée : **un `.h5p` peut ne contenir aucune bibliothèque**. Il n’a alors que `h5p.json` et `content/`, ressemble à un paquet complet, et ne jouera jamais seul. Le paquet du pilote lui-même est de cette forme. La commande le signale explicitement au lieu de répondre « rien à ajouter ».

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
ADR acceptée. État au 15 août 2026, après la clôture de l’étape 11.

| # | Condition | État | Où |
|---|---|---|---|
| 1 | Paquets privés avant validation | Remplie | Buckets privés depuis l’étape 03 ; aucune réponse n’expose de clé d’objet (08.3) |
| 2 | Quarantaine, extraction sécurisée, limites, MIME et antivirus | **Partielle** | 08.2 lit l’archive sans jamais l’extraire, refuse chemins remontants et absolus, plus de 500 entrées, les bombes de décompression et les fichiers de plus de 20 Mo. **Aucun antivirus**, faute de scanner dans l’environnement de stage |
| 3 | Bibliothèques figées comme artefacts internes | Remplie | Déploiement `PRE-01`, avec inventaire des empreintes : un artefact que personne ne peut nommer n’est pas figé |
| 4 | Aucun CLI H5P dans le chemin de production | Remplie | Ni éditeur ni CLI ; l’enregistrement est une commande du projet (08.2) |
| 5 | Runtime isolé par iframe et origine dédiée à CSP restrictive | Remplie | Origine `content` servie par nginx, `PRE-01` |
| 6 | Endpoint xAPI authentifié et autorisé | Remplie | Étape 11, `POST /api/v1/me/xapi/statements`. Authentifié par la session Élève, autorisé par le ticket de contenu, tentative déduite du ticket et jamais nommée par le client. ADR-014 |
| 7 | Date de réception serveur distincte du timestamp source | Remplie | `attempt_responses.recorded_at` (10.1) et, pour un événement, `xapi_statements.issued_at` — ce que la source prétend — à côté de `received_at`, horloge du serveur (11.1) |
| 8 | Licence et provenance vérifiées avant publication | **Partielle** | Les champs existent et ne sortent jamais par HTTP ; rien ne les vérifie automatiquement |

## Conséquences

Le MVP peut avancer sans serveur H5P complet. Restent dus avant une mise en
production : l’antivirus de la condition 2 et la vérification de licence de la
condition 8. Ce sont les deux dernières conditions partielles ; plus aucune n’est
entièrement à faire.
