# Création et accès Enfant

## Périmètre

Cette page décrit la sous-étape 06.3 : création d'un profil Enfant, par le Parent
ou par l'Enfant lui-même, connexion de l'Enfant, et isolation familiale.
L'authentification Parent relève de 06.2 et n'est pas reprise ici.

## Règle structurante, l'unicité est familiale

Un Enfant est **obligatoirement rattaché à un Parent**, et son pseudonyme est
unique **à l'intérieur de sa famille**, jamais à l'échelle de la plateforme. Deux
familles peuvent donc avoir chacune une `lea`, ce qui est indispensable : un
prénom d'usage ne peut pas être réservé au premier inscrit.

La conséquence est immédiate : **le pseudonyme ne désigne plus personne à lui
seul**. Tout accès Enfant part donc d'une famille, soit celle de la session
Parent qui appelle, soit celle que désigne le code famille saisi.

Cette règle prime sur l'extrait de code d'ADR-005, qui montrait une connexion
Enfant par pseudonyme et PIN seuls. C'est l'ADR qui reste à amender.

## Le code famille

Le code famille est l'identifiant public du Parent, celui qu'un Enfant saisit.
Il est tiré au hasard à l'inscription du Parent et rendu dans son profil.

- **Six caractères**, dans un alphabet de trente et un symboles d'où sont retirés
  le zéro et le O, le un, le I et le L : le code est lu sur une feuille ou dicté,
  pas copié-collé. Cela laisse plus de huit cents millions de combinaisons.
- **Ni l'email ni la clé primaire.** Ces deux-là ne doivent jamais circuler sur un
  écran de connexion Enfant : l'un est une donnée de contact de l'adulte, l'autre
  un identifiant technique de trente-six caractères qu'aucun enfant ne recopie.
- **Tiré au hasard et non dérivé du Parent**, donc il peut être remplacé s'il
  fuite, sans rien dire du compte qui est derrière.
- **Insensible à la casse** à la saisie, normalisé en majuscules.

Un tirage est vérifié contre les comptes existants avant d'être retenu, donc une
collision ne remonte jamais à l'appelant.

## Régénérer un code qui a fuité

`POST /api/v1/auth/parent/family-code/regenerate`, session Parent requise, tire un
nouveau code et rend le profil à jour. C'est la réponse à un code écrit sur un
cahier prêté, dicté au mauvais interlocuteur ou affiché sur une capture d'écran.

Trois effets, et trois seulement :

- **l'ancien code cesse immédiatement de fonctionner**, aussi bien pour la
  connexion, qui répond `401`, que pour l'auto-inscription, qui répond `404` ;
- **les sessions déjà ouvertes ne sont pas touchées.** L'enfant connecté sur la
  tablette familiale n'est pas la cause de la fuite, et le déconnecter
  transformerait une précaution en punition. Une session se révoque par la
  déconnexion, qui est déjà immédiate ;
- **les profils créés sous l'ancien code demeurent**, y compris ceux en attente.
  Supprimer un profil d'Enfant ne doit jamais être l'effet de bord d'une autre
  action ; c'est au Parent de décider lesquels il active.

La route est réservée au Parent : une session Enfant reçoit `403`, une requête sans
session `401`.

## Points d'entrée

| Méthode | Chemin | Rôle | Réponse |
|---|---|---|---|
| `POST` | `/api/v1/auth/parent/family-code/regenerate` | Remplacer un code qui a fuité | `200`, profil Parent |
| `POST` | `/api/v1/auth/children` | Créer un profil, session Parent requise | `201`, profil `active` |
| `POST` | `/api/v1/auth/child/register` | Créer un profil avec le code famille, sans session | `201`, profil `pending` |
| `GET` | `/api/v1/auth/children` | Lister les enfants du Parent connecté | `200`, profils en attente inclus |
| `POST` | `/api/v1/auth/children/{id}/activate` | Activer un profil en attente | `200`, profil `active` |
| `POST` | `/api/v1/auth/child/login` | Ouvrir une session Enfant | `200`, profil et cookie |
| `GET` | `/api/v1/auth/child/me` | Lire l'Enfant connecté | `200`, profil public |

La déconnexion reste `DELETE /api/v1/auth/logout` : la route ne lit que le jeton,
jamais l'identité derrière lui, donc elle sert les deux types de session sans
modification.

Le profil public d'un Enfant contient `id`, `pseudonym`, `display_name`,
`date_of_birth`, `status` et `created_at`. Comme `ParentPublic`, le schéma
`ChildPublic` ne déclare pas `pin_hash` : le champ est absent par construction et
non par filtrage.

## Trois états, une seule question

Un profil porte un `status` plutôt qu'un booléen, parce que la question « ce
profil peut-il ouvrir une session » a trois réponses et non deux :

| État | Origine | Peut se connecter |
|---|---|---|
| `active` | créé par le Parent, ou activé par lui | oui |
| `pending` | créé par l'Enfant avec le code famille | non, `403` explicite |
| `disabled` | désactivation, prévue pour une étape ultérieure | non, `401` muet |

Un profil `pending` créé par un enfant attend son Parent. Le message est explicite,
mais **seulement après un PIN correct** : celui qui n'a pas les identifiants
n'apprend rien de l'existence du profil. Un profil `disabled` ne dit rien du tout,
puisque la désactivation est une décision qui n'a pas à être annoncée.

C'est ce qui rend l'auto-inscription sûre : **connaître un code famille permet de
demander à rejoindre une famille, jamais d'y entrer**.

## Identifiants de l'Enfant

L'Enfant n'a ni email ni téléphone, conformément à ADR-005 : rien dans le profil
ne permet de le contacter. Il dispose d'un pseudonyme et d'un PIN.

Le pseudonyme est normalisé en minuscules, limité aux lettres ASCII, chiffres,
tiret et souligné, jamais aux extrémités, entre 3 et 50 caractères. La base impose
déjà le plancher de 3 caractères ; le motif ajoute ce que SQL n'exprime pas et
évite que deux pseudonymes ne diffèrent que par une ponctuation invisible.

Le PIN fait exactement six chiffres, comme le fixe ADR-005. Sont refusés à la
création le chiffre répété et la suite strictement croissante ou décroissante, qui
sont les premiers codes essayés par un attaquant et ceux qu'un parent pressé
choisit.

## Hachage du PIN

Le PIN est haché en **Argon2id**, avec les mêmes paramètres que les mots de passe
Parent. Un PIN de six chiffres ne représente qu'un million de combinaisons : le
coût par essai est donc l'une des deux seules protections, l'autre étant le verrou
décrit plus bas. Comme pour les mots de passe, une connexion réussie remplace une
empreinte produite sous d'anciens paramètres.

## Verrou sur les tentatives

Sans plafond, un script épuise un million de combinaisons ; le coût d'Argon2id
seul ne suffit pas à l'en empêcher. Un compteur d'échecs par enfant est donc tenu
dans Redis, sous la clé `child-pin-failures:<id>` :

- chaque échec incrémente le compteur et repousse l'expiration, donc la fenêtre
  glisse : un attaquant qui insiste maintient le verrou au lieu de l'attendre ;
- au-delà de `CHILD_PIN_MAX_ATTEMPTS`, la connexion répond `429` avant même de
  vérifier le PIN. Le bon PIN est refusé lui aussi : sans cela, le plafond ne
  ferait que ralentir l'attaque au lieu de l'arrêter ;
- une connexion réussie efface le compteur ;
- le compteur vit dans Redis et non dans PostgreSQL parce que c'est un état court
  qui doit expirer seul, exactement ce qu'une clé à durée de vie fait déjà.

La contrepartie est qu'un tiers connaissant un code famille et un pseudonyme peut
verrouiller cet enfant en épuisant les tentatives. Le verrou reste donc
temporaire, quinze minutes par défaut, plutôt que définitif : la gêne se mesure en
minutes, là où un verrouillage durable demanderait une intervention du Parent.

## Session Enfant

La session Enfant réutilise entièrement le socle de 06.2 : jeton opaque de 32
octets, clé Redis `session:<sha256(jeton)>`, cookie `HttpOnly`, `SameSite=lax`,
`Path=/`, et `Secure` piloté par l'environnement. Deux différences seulement :

- `user_type` vaut `child` et non `parent` ;
- la session vit **un jour** au lieu de sept, comme le prévoit ADR-005. Un poste
  partagé en famille ne doit pas garder un profil ouvert une semaine.

## Isolation familiale

L'isolation est une propriété des requêtes, pas une promesse écrite :

- la création rattache l'enfant à `parent.id` pris dans la session, ou au parent
  que désigne le code famille, jamais à un identifiant fourni par le client ;
- la liste filtre sur `Child.parent_id == parent.id`, donc un Parent ne voit que
  ses enfants ;
- l'activation ne retrouve un profil que dans la famille de l'appelant. Un profil
  d'une autre famille répond exactement comme un profil inexistant, `404`, donc la
  route ne peut pas servir à sonder les autres familles ;
- une session Enfant sur une route Parent répond `403`, et l'inverse aussi. Les
  deux espaces montrent des données différentes ; une route acceptant les deux
  types de session serait à un oubli de contrôle près d'afficher le tableau de
  bord Parent à un enfant.

## Non-divulgation

Un PIN erroné, un pseudonyme inconnu et un code famille inconnu renvoient
exactement la même réponse, `401` avec le message `Identifiants invalides`. Quand
aucun profil ne correspond, une vérification est menée contre une empreinte
factice, afin que le temps de réponse ne trahisse pas l'existence du profil. À la
connexion, ni le code ni le pseudonyme ne sont contrôlés dans leur forme :
appliquer les règles de format répondrait `422` à une saisie malformée et `401` à
une saisie inconnue, ce qui distinguerait deux cas qui doivent se ressembler.

L'auto-inscription fait exception : un code famille inconnu répond `404`. Un
enfant qui se trompe en recopiant son code doit pouvoir le comprendre, et
l'alternative, accepter silencieusement une inscription qui n'arrivera jamais à
son parent, serait pire. Ce que cette réponse révèle, c'est qu'un code existe ;
elle ne dit rien de la famille derrière, et elle ne permet que de créer un profil
en attente, sans accès.

## Limites assumées

- **Rien ne plafonne les profils en attente.** Un tiers connaissant un code
  famille peut créer des profils `pending` en série. Aucun n'ouvre de session, mais
  la liste du Parent se remplit. Un plafond par famille et une notification
  relèvent de l'étape des notifications et de l'étape 15.
- **Le retour arrière de la migration est conditionnel.** Le `downgrade` de
  `0003_family_code_child_status` rétablit l'unicité globale du pseudonyme, ce qui
  est impossible si deux familles en partagent déjà un. La migration s'arrête alors
  avec un message qui le dit, plutôt que de renommer des profils dans le dos de
  leurs familles : ces doublons doivent être arbitrés à la main avant de rejouer le
  retour arrière.
- **Aucune gestion du cycle de vie du profil.** Ni modification, ni désactivation,
  ni suppression, ni changement de PIN. L'état `disabled` existe dans le modèle
  mais aucune route ne le pose. C'est la limite la plus gênante après une fuite de
  code : le Parent régénère son code, mais ne peut pas encore écarter les profils
  en attente qui auraient été créés entre-temps.
- **Verrou par enfant et non par origine.** Le compteur ne distingue pas
  l'appelant : il protège un profil, pas le service. Une limitation de débit
  générale reste le point ouvert n°3 de `points-ouverts-authentification.md`.

## Configuration

| Variable | Défaut | Rôle |
|---|---|---|
| `CHILD_SESSION_TTL_SECONDS` | `86400` | Durée de vie d'une session Enfant, un jour |
| `CHILD_PIN_MAX_ATTEMPTS` | `5` | Échecs tolérés avant verrouillage |
| `CHILD_PIN_LOCKOUT_SECONDS` | `900` | Durée du verrou, fenêtre glissante |
