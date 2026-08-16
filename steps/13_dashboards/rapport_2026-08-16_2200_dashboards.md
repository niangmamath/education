# Rapport de réalisation

## Métadonnées

- Étape : 13, tableaux de bord
- Sous-étapes : 13.1, 13.2, 13.3 et 13.4
- Date et heure : 16 août 2026, 22h00
- Agent : Claude Code
- ID du planning : DASH-01 à DASH-04
- Branche : `feat/etape-13-dashboards`
- Commit ou pull request : Pull Request unique vers `main`
- Statut : Terminé

## Objectif

Alimenter les deux espaces avec les données réelles de l'API, et refermer par là
le point ouvert que l'étape 11 avait laissé : un endpoint xAPI que personne
n'appelait.

## Prérequis vérifiés

- Étapes 01 à 12 clôturées, migration `0012`, 559 tests, CI verte sur `main`.
- Dépôt propre, aucun `TODO` ni `FIXME` dans `apps/api`.
- Points ouverts relus : tous reportés vers une étape nommée ou vers la
  production ; aucun ne bloque cette étape.

## État initial observé

Le web était le prototype de l'étape 05 : des pages Bootstrap statiques, un
bandeau « données fictives » sur chacune, et pas une seule requête vers l'API.
Côté API, tout existait depuis six étapes et rien ne l'appelait.

## Travaux réalisés

### La décision qui gouverne l'étape, ADR-016

C'est la première fois que le web appelle l'API, donc la première fois qu'il faut
dire **comment**. La session est un cookie `HttpOnly` posé par l'API, et le web
vit sur une autre origine.

**Le navigateur ne connaît que l'origine du web.** Les composants serveur lisent
le cookie et appellent l'API eux-mêmes.

Un appel direct depuis le navigateur exigerait un cookie `SameSite=None; Secure`
voyageant comme cookie tiers — la forme même que les navigateurs suppriment — et
exposerait la session à tout ce que la page charge un jour. Le fait que
`localhost:3000` et `localhost:8000` soient « même site » rend le problème
invisible en développement et bien réel en production : une architecture qui ne
marche qu'en local est pire qu'une qui échoue partout, parce qu'elle échoue au
moment où c'est cher.

Un proxy générique a été écarté aussi : il ferait du web une seconde porte
d'entrée de l'API, chaque route devenant joignable par un chemin que personne n'a
écrit. Les mutations passent donc par des **actions serveur nommées une par une**.

Le garde d'accès est dans le layout et non dans un middleware, parce qu'un
middleware déciderait de la seule présence du cookie — et un cookie dont Redis ne
détient plus la session ressemble exactement à un cookie valide.

`GET /api/v1/auth/session` a été ajouté : sans lui, un client devrait essayer la
route Parent, lire un `403` et essayer la route Élève.

### 13.1, espace Élève

Cinq pages sur données réelles. **L'activité en cours passe avant tout** : c'est
le seul élément réellement urgent, et l'enterrer sous la liste de ce qui reste
serait le plus sûr moyen qu'elle ne soit jamais finie.

**Aucun diagnostic nulle part** : ni score, ni lacune, ni nom de règle. Ce sont
des activités et des durées. Ses résultats et sa progression restent à sa
disposition, et chacun porte la phrase qui l'explique.

Rien n'est classé par gravité : une page qui s'ouvrirait sur les échecs serait
une page sur l'échec.

### Le point ouvert de l'étape 11, refermé

`play.html` remontait ses événements xAPI par `postMessage` depuis le prérequis
`PRE-01`, sans destinataire. Le voici.

`POST /api/xapi` est la **seule** route d'API du web, et elle relaie sans rien
décider : elle lit le cookie, passe l'énoncé tel quel, met le ticket dans
l'en-tête, et rend `202` ou une erreur sans dire laquelle.

**Le contrôle d'origine du `postMessage` est la mesure de sécurité de cette
boucle.** `postMessage` livre à une fenêtre, pas à un destinataire : n'importe
quelle frame, n'importe quelle extension peut poster dans la page. Sans
vérification de `event.origin`, n'importe quoi sur la machine pourrait déposer
des réponses au nom d'un enfant. L'origine attendue vient de l'URL de lecture
rendue par l'API, donc rien dans une requête ne peut la déplacer.

### 13.2, espace Parent

Six pages. Chaque conclusion porte la phrase qui l'a produite : un parent qui ne
peut pas discuter une conclusion se fait seulement dire quoi penser.

Les **lacunes reportées sont montrées à part**, avec ce qu'elles attendent, et ne
sont comptées ni dans les points d'attention ni dans les notifications : les
signaler pousserait vers la compétence que la plateforme a décidé de ne pas
travailler encore.

`/parent/parametres` publie les règles de lecture et de diagnostic. C'est la page
pour laquelle elles ont été publiées, et elle dit pourquoi il n'y a rien à régler
plutôt que d'afficher des interrupteurs sans effet.

### 13.3, notifications

Lecture stricte du « sans automatisme trompeur », et assumée : **rien n'est
envoyé nulle part**. Aucun e-mail, aucune alerte, rien de stocké, aucun état
« lu » — donc **pas de pastille de non-lus**, parce qu'une pastille
revendiquerait un état que personne ne tient.

Ce qui existe est une relecture de faits qu'un parent aurait trouvés en ouvrant
trois pages. La page le dit en toutes lettres.

Le calcul est fait côté web et non dans l'API : un modèle de notification, avec
sa remise, ses canaux et son état de lecture, est le sujet de l'étape 14, et en
inventer la moitié maintenant laisserait cette étape discuter avec une
demi-implémentation.

### 13.4, clôture

La boucle du MVP a été jouée **de bout en bout sur la pile vivante**, et c'est la
preuve qui compte pour cette étape.

## Fichiers créés

- `apps/web/lib/api.ts`, `types.ts`, `session.ts`, `actions.ts`, `notifications.ts`
- `apps/web/app/api/xapi/route.ts`
- `apps/web/app/eleve/activites/[assignmentId]/page.tsx` et `resultat/page.tsx`
- `apps/web/components/auth/login-forms.tsx`
- `apps/web/components/eleve/content-player.tsx`, `start-activity-button.tsx`,
  `finish-attempt-button.tsx`
- `apps/web/components/parent/notification-list.tsx`,
  `apply-remediation-button.tsx`
- `apps/web/components/ui/sign-out-button.tsx`
- `docs/adr/ADR-016-web-parle-a-l-api-par-le-serveur.md`
- `docs/backend/dashboards.md`

## Fichiers modifiés

- `apps/api/app/api/v1/auth.py`, `app/schemas/auth.py` : `GET /auth/session`
- `apps/api/tests/test_auth_parent.py` : trois tests de plus
- `apps/web` : les deux layouts, les deux en-têtes, `/connexion`, et les huit
  pages des deux espaces
- `docs/architecture/decision-register.md`
- `steps/ETAT.md`, `steps/PLANNING.md`, les quatre fiches de l'étape

## Commandes exécutées

```
ruff format --check . && ruff check . && mypy app && pytest -q
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
pnpm --filter @studentconnect/web run build
```

## Preuves sur la pile vivante

Une famille réelle a été créée, une activité H5P publiée, et la boucle jouée
contre l'API et le web réellement démarrés.

```text
/eleve sans session                       307 vers /connexion
/eleve avec session Élève                 « Bonjour, Léa E2E », activité affichée
page de lecture                           iframe vers localhost:8081/player/play.html
                                          avec l'empreinte du contenu et un ticket
POST /api/xapi (énoncé answered)          202, {"received":true}
POST /api/xapi (même énoncé rejoué)       202, un seul énoncé stocké
énoncé stocké                             acteur pseudonyme 9433a6c8…,
                                          « Léa Dupont » revendiqué absent
tentative terminée                        « 1 réponse évaluée, dont 1 juste », acquise
/parent/enfants/{id}                      santé académique 100, sa phrase, aucune
                                          difficulté à confirmer
```

Les données de cette vérification ont été supprimées après coup.

## Résultats des tests

```text
Ruff        : vert, format inclus
Mypy        : vert sur 72 fichiers
Pytest      : 562 tests réussis, dont 3 pour GET /auth/session
TypeScript  : vert
ESLint      : vert
Build Next  : vert, 19 routes
```

## Critères d'acceptation

- [x] Espace Élève sur données réelles : activité à reprendre, progression,
      actions adaptées.
- [x] Espace Parent sur données réelles : enfants autorisés, activités, progrès,
      points d'attention explicables.
- [x] Notifications présentées sans automatisme trompeur.
- [x] Contrôles d'autorisation et d'isolation : garde par espace, session de
      l'autre espace renvoyée, absence de session redirigée.
- [x] TypeScript, ESLint et build Next.js verts, le web étant modifié.
- [x] Ruff, Mypy et Pytest verts.
- [x] Une seule Pull Request pour toute l'étape.

## Décisions ou ADR

ADR-016, acceptée. Elle consigne les décisions prises sans arbitrage : l'appel
par le serveur plutôt que par le navigateur, les actions nommées plutôt qu'un
proxy générique, le garde dans le layout plutôt que dans un middleware, et la
seule route d'API du web.

## Écarts par rapport au prompt

Aucun sur le périmètre. `GET /auth/session` a été ajouté à l'API alors que
l'étape porte sur le web : sans lui le web devrait provoquer un `403` pour savoir
qui il sert.

## Risques ou dette technique

- **Aucun test automatisé du web.** La CI tient TypeScript, ESLint et le build ;
  les parcours ont été éprouvés à la main. C'est la dette principale de l'étape,
  et elle est réelle : un rendu qui régresse ne sera vu par personne. `vitest`
  est déclaré dans `package.json` sans être installé ni lancé par la CI, ce qui
  est le point de départ naturel pour la résorber.
- **Un appel d'API par enfant** sur le tableau de bord Parent. À la taille d'une
  famille cela ne se mesure pas ; à celle d'une classe, il faudra une lecture
  groupée.
- **Aucun écran d'administration des profils** : créer, activer, désactiver un
  enfant restent des appels d'API. C'est l'étape 15.
- Le bandeau « prototype » a disparu des pages alimentées, mais
  `/eleve/recompenses` le garde : rien ne calcule de récompense et une page qui
  en montrerait mentirait.

## Blocages

Aucun.

## Prochaines actions

Étape 14, notifications. Le modèle, la remise et l'état de lecture y sont
entiers ; la page « Ce qui a changé » de cette étape en est la présentation
provisoire et devra s'y raccorder.

## Mise à jour appliquée à ETAT.md

Section « Étape 13, tableaux de bord, clôturée », résultats techniques, point
ouvert de l'étape 11 marqué refermé, prochaine action.

## Mise à jour appliquée à PLANNING.md

Phase 9 créée, DASH-01 à DASH-04 à « Terminé » avec leurs preuves.
