# Authentification Parent et sessions

## Périmètre

Cette page décrit la sous-étape 06.2 : inscription d'un compte Parent, connexion,
session serveur et déconnexion. L'accès Enfant relève de 06.3 et n'est pas traité
ici.

## Points d'entrée

| Méthode | Chemin | Rôle | Réponse |
|---|---|---|---|
| `POST` | `/api/v1/auth/parent/register` | Créer un compte Parent | `201` avec le profil public |
| `POST` | `/api/v1/auth/parent/login` | Ouvrir une session | `200` avec le profil public et le cookie |
| `DELETE` | `/api/v1/auth/logout` | Révoquer la session | `204` sans corps |
| `GET` | `/api/v1/auth/me` | Lire le Parent connecté | `200` avec le profil public |

Le profil public ne contient que `id`, `email`, `display_name`, `is_verified` et
`created_at`. Le schéma `ParentPublic` ne déclare pas `password_hash` : le champ est
absent par construction et non par filtrage, donc aucune modification ultérieure de
la route ne peut le laisser fuir.

## Hachage des mots de passe

Les mots de passe sont hachés avec **Argon2id**, via `argon2-cffi` et ses paramètres
par défaut, qui suivent le profil recommandé par la RFC 9106. Argon2id est
l'algorithme placé en tête des recommandations OWASP, devant bcrypt, parce que son
coût mémoire rend l'attaque par matériel dédié beaucoup plus chère.

ADR-005 mentionnait bcrypt dans un extrait de code illustratif, mais sa section
Décision ne fixe aucun algorithme. Le choix d'Argon2id est donc un choix
d'implémentation à confirmer dans l'ADR.

Trois conséquences pratiques :

- chaque hachage porte son propre sel, donc deux comptes partageant le même mot de
  passe produisent des empreintes différentes ;
- à chaque connexion réussie, `check_needs_rehash` détecte une empreinte produite
  sous d'anciens paramètres et la remplace : c'est le seul instant où le mot de
  passe en clair est disponible pour cette opération ;
- un mot de passe fait entre 12 et 128 caractères. Le plancher suit OWASP ASVS ; le
  plafond n'existe que pour éviter qu'une requête ne fasse hacher une charge
  arbitrairement grande.

## Sessions opaques

Conformément à ADR-005, aucune table SQL de session n'est créée. Une session est
uniquement une entrée Redis :

- le jeton est tiré par `secrets.token_urlsafe(32)`, soit 32 octets aléatoires ;
- la clé Redis est `session:<sha256(jeton)>` et non `session:<jeton>`. Une copie de
  la base Redis ne livre donc aucun cookie rejouable. Un SHA-256 simple suffit ici
  parce que le jeton est déjà de l'aléa pur et non un secret à faible entropie ;
- la valeur est un hash Redis contenant `user_id`, `user_type` et `expires_at` ;
- l'expiration est portée par Redis lui-même, avec une durée de vie de sept jours ;
- chaque connexion crée un nouveau jeton, ce qui ferme la fixation de session
  listée dans les risques d'ADR-005 ;
- la déconnexion supprime la clé, donc une session est révocable immédiatement,
  côté serveur, sans attendre son expiration.

## Cookie

Le cookie `studentconnect_session` est posé avec `HttpOnly`, `SameSite=lax`,
`Path=/` et `Max-Age` aligné sur la durée de vie de la session. L'attribut `Secure`
est piloté par `SESSION_COOKIE_SECURE` : laissé vide, il est actif partout sauf en
développement local. Une variable d'environnement oubliée échoue donc du côté sûr
plutôt que d'exposer le cookie en clair.

## Non-divulgation

Un mot de passe erroné et une adresse inconnue renvoient exactement la même réponse,
`401` avec le message `Identifiants invalides`. Quand aucun compte ne correspond à
l'adresse, une vérification est tout de même effectuée contre une empreinte factice,
afin que le temps de réponse ne trahisse pas l'existence du compte.

L'inscription fait exception : une adresse déjà prise renvoie `409`. Ce point révèle
qu'un compte existe, mais l'alternative, accepter silencieusement une inscription en
double, rendrait le parcours incompréhensible. Le contournement habituel, confirmer
par email sans rien dire dans la réponse, suppose un envoi d'emails qui n'existe pas
encore.

## Limites assumées

- **Vérification d'adresse email non implémentée.** ADR-005 place une étape de
  vérification entre l'inscription et la connexion. L'infrastructure ne comporte
  aucun service d'envoi d'emails, donc `is_verified` reste à `false` et la connexion
  ne l'exige pas. Exiger la vérification aujourd'hui rendrait toute connexion
  impossible. Ce point devra être repris quand un service d'envoi existera.
- **Client Redis créé par requête.** Un client asyncio mémorise la boucle
  d'événements de sa première commande, ce qui casse dès qu'une autre boucle
  l'utilise. Un client par requête évite ce piège au prix d'une connexion par
  requête ; la mise en pool relève de l'étape d'exploitation.
- **Pas de limitation de débit sur la connexion.** Rien ne freine aujourd'hui une
  attaque par force brute au-delà du coût d'Argon2id. Les réglages `RATE_LIMIT`
  existent dans la configuration mais ne sont branchés nulle part.

## Configuration

| Variable | Défaut | Rôle |
|---|---|---|
| `SESSION_COOKIE_NAME` | `studentconnect_session` | Nom du cookie de session |
| `SESSION_COOKIE_SAMESITE` | `lax` | Valeur de l'attribut `SameSite` |
| `SESSION_COOKIE_SECURE` | vide | Force `Secure` ; vide signifie actif hors développement |
| `SESSION_TTL_SECONDS` | `604800` | Durée de vie d'une session, sept jours |
