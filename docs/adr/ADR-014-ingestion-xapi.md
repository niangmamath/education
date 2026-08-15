# ADR-014, Ingestion xAPI liée au ticket, acteur pseudonyme, prééminence du runtime

- Statut : Accepté
- Date : 15 août 2026

## Contexte

Le runtime de contenu vit sur une origine séparée et ne détient aucun
identifiant : c'est la mesure de sécurité d'ADR-012, condition 5. `play.html`
remonte les événements xAPI à la page qui l'héberge par `postMessage`, et
jusqu'à l'étape 11 personne ne les recevait. La condition 6 d'ADR-012 demande un
« endpoint xAPI authentifié et autorisé » ; c'est la dernière condition entière
qui restait à faire.

Trois questions se posaient ensemble, et elles ne se répondent pas séparément.

1. **Qui a le droit d'envoyer un événement, et pour quel travail ?** Le runtime
   ne peut pas appeler l'API : il n'a ni cookie, ni clé, ni adresse. Le
   navigateur, lui, le peut — mais un navigateur peut envoyer n'importe quoi.
2. **Quel acteur écrire ?** Un événement xAPI porte un champ `actor`. Le
   runtime, à qui l'on ne dit rien, y met ce qu'il veut ; un client malveillant
   aussi.
3. **Qui a raison quand le navigateur et le runtime décrivent la même
   question ?** Depuis l'étape 10, `attempt_responses.source` distingue
   `declared` de `xapi`. La colonne existait ; la règle, non.

## Décision

### L'événement est autorisé par le ticket, et la tentative est déduite

`POST /api/v1/me/xapi/statements` exige **deux choses à la fois** : la session
Élève, par le cookie, et le **ticket de contenu**, dans l'en-tête
`X-Content-Ticket`. Le ticket est celui qu'ADR-012 et le prérequis `PRE-01` ont
déjà mis en place : une valeur opaque frappée par le serveur quand l'enfant
ouvre une activité, gardée trente minutes dans Redis, qui nomme une affectation
et un contenu.

Le client **ne nomme jamais la tentative**. Le serveur la déduit du ticket :
ticket → affectation → tentative en cours. Un client qui pourrait désigner la
tentative pourrait déposer une observation sur un autre travail.

L'affectation du ticket est vérifiée contre l'enfant de la session. Les tickets
sont opaques et non devinables, donc c'est une défense en profondeur ; c'est
aussi ce qui rend la garantie vraie par construction plutôt que par
raisonnement.

Le ticket voyage dans un en-tête et non dans le corps : il n'est pas une partie
de l'événement, et un événement qui porterait sa propre autorisation serait à
une falsification près d'être sa propre permission.

### L'acteur revendiqué est jeté, et remplacé par un pseudonyme du serveur

Quoi que l'événement mette dans `actor`, il ne survit pas à l'ingestion. Le
serveur écrit à la place un agent pseudonyme dont le nom de compte est
`HMAC-SHA256(SECRET_KEY, "xapi-actor:" + identifiant de l'enfant)`.

Le raisonnement tient en une phrase : **le runtime ne reçoit aucune identité,
donc rien de ce qu'il nomme là n'est une identité que nous lui ayons donnée.**
Conserver le champ revendiqué laisserait un navigateur écrire un vrai nom dans
notre base par un champ que personne ne lit.

La clé est dérivée avec le secret de l'application pour qu'une copie de la base
ne se lise pas comme une liste d'enfants. Faire tourner le secret change le
pseudonyme et ne casse rien : ce qui relie un événement à un enfant est la clé
étrangère sur la tentative, jamais cette valeur.

### Un événement du runtime prime sur une réponse déclarée

Quand les deux décrivent la même question, la lecture retient l'événement du
runtime, **quel que soit l'ordre d'arrivée**. Entre deux sources de même nature,
la plus récente l'emporte toujours : répondre deux fois reste deux réponses.

Ce n'est pas une affirmation que l'un serait plus difficile à falsifier que
l'autre — les deux passent par le même navigateur. C'est une question de **qui a
interprété**. Une réponse `declared` est la conclusion du client sur ce qui s'est
passé ; une réponse `xapi` est le compte rendu du contenu, relayé tel quel et lu
par le serveur. Ce sont deux récits d'un même fait, pas deux faits, et celui que
le serveur a lui-même lu est celui qu'il garde.

L'ordre inverse aurait une conséquence désagréable : un client pourrait défaire
un événement du runtime en publiant sa propre déclaration juste après.

### Les événements sont conservés, et les rejeux reconnus

Une table `xapi_statements` garde l'événement tel que reçu — acteur déjà
remplacé —, son verbe, son objet, ce que le contenu a conclu, l'horodatage que la
source prétend et celui du serveur. `(attempt_id, statement_id)` est unique :
une retransmission est reconnue au lieu d'être comptée deux fois. L'unicité est
portée par la tentative et non globale, sinon une famille pourrait faire taire
l'événement d'une autre en réservant son identifiant la première.

L'identifiant est **exigé** de l'émetteur. Le frapper ici ferait de chaque
réessai un second événement. `play.html` en pose un quand le contenu n'en fournit
pas.

Seul le verbe `answered` devient une réponse. Les autres verbes autorisés sont
conservés et ne concluent rien : ils parlent de la séance, pas d'une question.
Un verbe inconnu est **refusé**, parce que la fiche demande des événements
*autorisés* et qu'un événement que nous n'avons jamais vu n'est pas un événement
que nous pouvons prétendre avoir compris.

### Les agrégats de progrès ne sont pas stockés

`GET /api/v1/me/progress` et `GET /api/v1/children/{id}/progress` calculent à
chaque lecture, à partir des résultats déjà écrits et des événements reçus.
Aucune table d'agrégats.

C'est ce qui rend les agrégats **reproductibles** au sens que l'étape demande :
les mêmes faits donnent la même réponse, et il n'existe pas une quatrième chose
capable de contredire les trois dont elle est tirée. Le prix est quelques
requêtes par lecture, sur des volumes d'une famille. Si les tableaux de bord de
l'étape 13 ont besoin d'un cache, ce sera une décision de cache prise au grand
jour, pas une duplication silencieuse de la vérité.

**Les résultats sont sommés, jamais recalculés.** La lecture d'une tentative a
été faite à sa clôture, avec l'attribution question-compétence telle qu'elle
était alors. Recalculer appliquerait l'attribution d'aujourd'hui aux réponses
d'hier et changerait sans le dire une conclusion déjà montrée à un parent.

## Conséquences

- ADR-012 condition 6 est remplie ; son tableau de suivi le consigne.
- Les réponses `declared` restent acceptées. Le contenu n'est pas obligé
  d'émettre du xAPI, et une activité qui n'en émet pas n'est pas privée de
  lecture.
- Le web devra, à l'étape 13, écouter le `postMessage` de `play.html` et relayer
  vers cet endpoint avec le ticket qu'il détient déjà. L'API est prête ; aucun
  client ne l'appelle encore.
- Faire tourner `SECRET_KEY` change tous les pseudonymes d'acteur. Les
  événements antérieurs restent rattachés à leur tentative, mais leur `actor_key`
  ne correspondra plus à celui calculé après rotation. C'est accepté : cette
  valeur n'est pas une clé de jointure.
