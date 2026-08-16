# ADR-016, Le web parle à l'API par son serveur, jamais par le navigateur

- Statut : Accepté
- Date : 16 août 2026

## Contexte

L'étape 13 est la première où le web appelle l'API. Jusqu'ici il n'était qu'un
prototype d'interface, et la question de savoir *comment* il l'appellerait
n'avait jamais eu à se poser.

Elle se pose maintenant, et elle est structurante, parce que la session est un
**cookie `HttpOnly`** posé par l'API (ADR-005) et que le web vit sur une autre
origine : `localhost:3000` face à `localhost:8000` en développement, deux noms
distincts en production.

Trois choix étaient possibles :

1. le navigateur appelle l'API directement ;
2. le web relaie tout par un proxy générique ;
3. le web appelle l'API depuis son propre serveur, et le navigateur ne connaît
   que l'origine du web.

## Décision

**Le navigateur ne connaît que l'origine du web.** Les composants serveur de
Next.js lisent le cookie de session et appellent l'API eux-mêmes ; le navigateur
ne détient ni identifiant d'API, ni adresse d'API, ni jeton.

### Pourquoi pas l'appel direct

Le cookie devrait alors être `SameSite=None; Secure` et voyager comme cookie
tiers — exactement la forme que les navigateurs sont en train de supprimer. Et
il faudrait qu'il soit lisible par du script, ou que chaque requête l'accompagne
sur une origine tierce : dans les deux cas la session se retrouve exposée à tout
ce que la page charge un jour.

Le fait que `localhost:3000` et `localhost:8000` soient « même site » en
développement rend le problème invisible en local et bien réel en production.
Une architecture qui ne marche qu'en développement est pire qu'une architecture
qui échoue partout : elle échoue au moment où c'est cher.

### Pourquoi pas un proxy générique

Un `/api/[...path]` qui relaie tout ferait du web une seconde porte d'entrée de
l'API, avec sa propre surface : chaque route de l'API deviendrait joignable par
un chemin que personne n'a écrit et que rien ne teste.

Les mutations passent donc par des **actions serveur** nommées une par une —
se connecter, commencer une activité, terminer une tentative, donner les
remédiations proposées. Ce qui n'a pas d'action n'est pas atteignable.

### La seule exception, et pourquoi elle est nécessaire

`POST /api/xapi` est la seule route d'API du web. Elle existe parce que seul le
navigateur est en position de relayer ce que le runtime de contenu dit : le
contenu vit sur une troisième origine, il remonte ses événements xAPI par
`postMessage`, et aucun serveur n'est dans la boucle.

Elle relaie et ne décide rien : elle lit le cookie, passe l'énoncé tel quel,
met le ticket dans l'en-tête, et rend `202` ou une erreur sans dire laquelle.
Elle ne pourrait pas autoriser quoi que ce soit — elle ne détient aucune règle.

**Le contrôle d'origine du `postMessage` est la mesure de sécurité de cette
boucle.** `postMessage` livre à une fenêtre, pas à un destinataire : n'importe
quelle frame, n'importe quel ouvreur, n'importe quelle extension peut poster
dans la page. Sans vérification de `event.origin`, n'importe quoi sur la machine
pourrait déposer des réponses au nom d'un enfant. L'origine attendue est tirée
de l'URL de lecture rendue par l'API, donc elle n'est pas paramétrable par une
requête.

### La connexion pose le cookie sur l'origine du web

L'API frappe la session ; l'action serveur lit le `Set-Cookie` et **repose** le
cookie sur l'origine du web, en réaffirmant ses attributs, `httpOnly` compris.
Relayer l'en-tête tel quel ne marcherait pas — il a été écrit pour l'hôte de
l'API — et surtout, réécrire les attributs à la main est ce qui garantit que
rien de la session ne devient lisible en changeant d'origine.

### Le garde d'accès est dans le layout, pas dans un middleware

Un middleware déciderait à partir de la présence du cookie, ce qui ne dit rien :
un cookie dont Redis ne détient plus la session ressemble exactement à un cookie
valide. Le layout demande à l'API, et **c'est l'API qui décide**. Le web
n'interprète jamais une session pour son compte.

Une session de l'autre espace est renvoyée vers son espace plutôt que vers la
page de connexion : un enfant qui atterrit sur une URL Parent n'est pas
déconnectée, elle est ailleurs.

### `GET /api/v1/auth/session`

Ajouté pour cette étape. Sans lui, un client devrait essayer la route Parent,
lire un `403` et essayer la route Élève — deux allers-retours et un refus dans
les journaux pour répondre à une question qu'aucune des deux n'a été conçue pour
entendre. Il ne rend que le type de session, l'identifiant et le nom affiché.

## Conséquences

- Le navigateur ne peut pas appeler l'API, même si quelqu'un le voulait : il n'en
  connaît pas l'adresse. `API_URL` est une variable du serveur, jamais
  `NEXT_PUBLIC_`.
- Toutes les pages des deux espaces sont rendues à la demande. Aucune n'est
  statique, et c'est correct : elles montrent des données d'une famille.
- Les lectures ne sont pas mises en cache, `cache: 'no-store'`. Un tableau de
  bord qui montrerait les lacunes d'hier serait pire qu'un tableau de bord qui
  prend un instant de plus.
- Le point ouvert de l'étape 11 est refermé : l'endpoint xAPI a enfin un
  appelant, et la boucle du MVP est jouable de bout en bout.
- Une charge réelle demanderait de revoir le nombre d'appels par page — le
  tableau de bord Parent en fait un par enfant. À la taille d'une famille, cela
  ne se mesure pas ; c'est écrit ici pour que la question soit posée avant, et
  non découverte après.
