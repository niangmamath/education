# Événements xAPI

Ce que le runtime de contenu raconte, comment cela parvient au serveur, et ce
que le serveur accepte d'en croire. Le runtime lui-même est décrit dans
`runtime-contenu.md` ; les tentatives et leur lecture dans
`tentatives-resultats.md` ; la décision est ADR-014, et cette étape remplit la
condition 6 d'ADR-012.

## Le chemin d'un événement

```
contenu H5P  ──(événement xAPI)──►  play.html
                                        │  postMessage, seul canal entre
                                        │  deux origines
                                        ▼
                              page de l'application
                                        │  POST /api/v1/me/xapi/statements
                                        │  cookie de session + X-Content-Ticket
                                        ▼
                                       API
```

`play.html` **ne parle jamais à l'API** et ne détient rien qui le lui
permettrait : ni cookie, ni clé, ni adresse. C'est la mesure de sécurité, pas
une gêne : un contenu qui se comporte mal n'a aucun accès à détourner.

La page de l'application, elle, est sur l'origine de l'API et porte le cookie de
session. C'est elle qui relaie, avec le ticket qu'elle détient déjà pour avoir
ouvert l'activité.

## Qui a le droit d'envoyer

Deux conditions à la fois, et le client ne choisit rien d'autre.

1. **Session Élève**, par le cookie. Un Parent est refusé : ce que fait un
   enfant dans un contenu n'est pas quelque chose qu'un parent puisse déclarer à
   sa place.
2. **Ticket de contenu**, dans l'en-tête `X-Content-Ticket`. C'est le ticket de
   `PRE-01` : opaque, frappé par le serveur quand l'enfant ouvre l'activité,
   valable trente minutes, il nomme une affectation et un contenu.

Le ticket voyage dans un en-tête et non dans le corps, parce qu'il n'est pas une
partie de l'événement. Un événement portant sa propre autorisation serait à une
falsification près d'être sa propre permission.

**La tentative est déduite, jamais nommée.** Le serveur va du ticket à
l'affectation, puis à la tentative en cours. Un client capable de désigner la
tentative pourrait déposer une observation sur un autre travail.

Toutes les raisons de refus liées au ticket rendent la même réponse `403` : pas
de ticket, ticket expiré, ticket d'une autre famille. La différence n'est utile
qu'à celui qui les essaie l'une après l'autre. Une seule réponse est distincte,
`409`, quand le ticket est bon mais qu'aucune tentative ne tourne : celle-là,
l'émetteur peut la corriger.

## Ce qui est refusé de l'événement lui-même

- **Sans `id`** : l'identifiant est ce qui rend un rejeu reconnaissable, et
  l'exiger est un choix. Le frapper côté serveur ferait de chaque réessai une
  seconde réponse. `play.html` en pose un quand le contenu n'en fournit pas.
- **Verbe hors liste.** Huit verbes sont acceptés, ceux que H5P émet. Un verbe
  jamais vu n'est pas un verbe que nous pouvons prétendre avoir compris.
- **Sans objet**, ou objet dont l'identifiant dépasse ce que
  `attempt_responses.question_ref` peut porter. **Refusé plutôt que tronqué** :
  raccourcir fusionnerait silencieusement deux questions en une.
- **Plus de 16 kio**, ou `result.success` qui n'est pas un booléen, ou
  `result.response` trop longue.

Un événement refusé ne laisse rien derrière lui.

## L'acteur, et ce qu'il n'est jamais

Un événement xAPI porte un champ `actor`. Il est **jeté**, et remplacé par un
agent que le serveur construit :

```json
{
  "objectType": "Agent",
  "account": {
    "homePage": "https://studentconnect.local/pseudonymes",
    "name": "<HMAC-SHA256(SECRET_KEY, \"xapi-actor:\" + identifiant enfant)>"
  }
}
```

Le raisonnement tient en une phrase : **le runtime ne reçoit aucune identité**,
donc rien de ce qu'il nomme là n'est une identité que nous lui ayons donnée.
Conserver le champ revendiqué laisserait un navigateur écrire un vrai nom dans
la base par un champ que personne ne lit.

La clé est dérivée avec le secret de l'application, pour qu'une copie de la base
ne se lise pas comme une liste d'enfants. Faire tourner le secret change le
pseudonyme et ne casse rien : ce qui relie un événement à un enfant est la clé
étrangère sur la tentative, jamais cette valeur.

Dans l'autre sens, l'URL de lecture ne porte qu'une empreinte de contenu et un
ticket. Ni l'identifiant de l'enfant, ni son pseudonyme, ni le code famille, ni
l'affectation. C'est éprouvé par un test, parce qu'une propriété d'isolation qui
n'est vérifiée par personne finit par ne plus être vraie.

## Ce qu'un événement devient

| Verbe | Effet |
|---|---|
| `answered` | Une ligne `attempt_responses` de provenance `xapi` |
| les sept autres | Conservé, ne conclut rien |

Seul `answered` parle d'une question. `completed`, `progressed` et les autres
parlent de la séance ; en faire des réponses inventerait des preuves.

**Un événement ne termine pas la tentative.** Terminer est un acte délibéré,
`POST /me/attempts/{id}/complete` ; une observation n'en est pas un.

`result.success` absent reste absent : un contenu qui ne dit pas si une réponse
est juste n'est pas contraint de le dire — la même règle que le chemin déclaré.

## Deux horloges

`issued_at` est ce que la source prétend ; `received_at` est l'horloge du
serveur. C'est la condition 7 d'ADR-012, et la raison en est que la première est
une preuve sur la source et seule la seconde une preuve sur le temps.

Un horodatage illisible est **abandonné plutôt que refusé** : il ne décide rien
ici, et perdre toute l'observation pour lui coûterait plus qu'il ne protège.

## Un rejeu n'est pas une seconde réponse

`(attempt_id, statement_id)` est unique. Le même événement renvoyé rend `200` et
l'enregistrement déjà tenu ; un événement nouveau rend `201`. Aucun des deux
n'est une erreur : un réessai sur un réseau capricieux est le même événement, et
le client est renseigné plutôt que mis en faute.

L'unicité est portée par la tentative et non globale. Globale, une famille
pourrait faire taire l'événement d'une autre en réservant son identifiant la
première.

## Routes

| Route | Qui | Ce qu'elle fait |
|---|---|---|
| `POST /api/v1/me/xapi/statements` | Élève + ticket | Reçoit un événement. `201` s'il est neuf, `200` si c'est un rejeu |
| `GET /api/v1/me/attempts/{id}/xapi/statements` | Élève | Ce qui a été reçu pour une de ses tentatives |

La lecture est réservée à l'enfant dont c'est la tentative, comme toute route
qui touche une tentative. Ce qu'un parent voit est la **lecture** — les progrès
de `progres.md`, les tableaux de bord de l'étape 13 — et non le trafic brut d'un
contenu que son enfant utilisait.

## Ce que l'étape 11 ne fait pas

- **Aucun client n'appelle encore cette route.** Le web reste le prototype de
  l'étape 05 ; brancher le `postMessage` de `play.html` sur cet endpoint est le
  travail de l'étape 13, quand le web parlera à l'API pour la première fois.
  L'API est prête et éprouvée par ses tests.
- **Aucun LRS.** Ce n'est pas un Learning Record Store : pas de `GET` par
  requête xAPI, pas de `voided`, pas d'`authority`, pas de version de spec
  négociée. C'est un récepteur pour les contenus du pilote, et le dire évite de
  laisser croire à une conformité que rien ne teste.
- **Aucun diagnostic.** C'est l'étape 12.
