# État du projet

## Référence

- Projet : StudentConnect
- Date : 13 août 2026
- Dépôt : `Tidianesarrndiaye/StudentConnect`
- Branche : `main`
- Version cible : `V0.1`

## Terminé

- [x] Dépôt reconstruit depuis zéro.
- [x] Fichiers racine et ADR initiaux.
- [x] Monorepo pnpm/Turborepo.
- [x] Frontend Next.js et Tailwind initialisé.
- [x] Backend FastAPI initialisé.
- [x] Environnement Python Linux `.venv` opérationnel.
- [x] Node.js et pnpm natifs Linux dans WSL.

## Étape 03, infrastructure locale et CI

- [x] Docker Compose validé de bout en bout.
- [x] PostgreSQL, Redis et MinIO opérationnels.
- [x] Les cinq buckets MinIO sont privés.
- [x] FastAPI et CORS validés.
- [x] Celery et la tâche de santé validés.
- [x] SQLAlchemy async et Alembic validés.
- [x] Ruff, Mypy et Pytest validés.
- [x] TypeScript, ESLint et build Next.js validés.
- [x] Script global `check_step03.sh` terminé avec le code `0`.
- [x] Rapports de l’étape 03 produits.
- [x] Commit principal créé et poussé : `d7a7262`.
- [x] Correctif Secret Scan créé et poussé : `6bcf765`.
- [x] API CI distante réussie.
- [x] Web CI distante réussie.
- [x] Secret Scan distant réussi après remplacement de l’action sous licence.
- [x] Étape 03 clôturée.

## Résultats techniques de référence

```text
PostgreSQL : healthy, base et rôle studentconnect
Redis      : healthy, PONG
MinIO      : healthy, cinq buckets privés
FastAPI    : healthy, /health/live → live
Celery     : pong, tâche studentconnect.health.ping réussie
Alembic    : 0001_infrastructure_baseline (head)
Ruff       : vert, format inclus
Mypy       : vert sur 11 fichiers
Pytest     : 12 tests réussis
TypeScript : vert
ESLint     : vert
Next.js    : build de production réussi
API CI     : succès
Web CI     : succès
Secret Scan: succès
```

## Historique de clôture

- `d7a7262` : infrastructure locale, migrations, contrôles qualité et workflows CI.
- `6bcf765` : remplacement de `gitleaks/gitleaks-action` par le scanner Gitleaks exécuté directement, sans dépendance à une licence d’organisation.
- La première exécution du Secret Scan sur `d7a7262` a échoué pour absence de licence Gitleaks d’organisation. Cet échec était un problème de configuration du workflow et non une détection de secret.
- L’exécution suivante du Secret Scan sur `6bcf765` a réussi.

## Organisation des étapes

Les dossiers détaillés des étapes 08 à 16 sont temporairement retirés du dépôt. Chaque dossier rejoint le dépôt au démarrage de l’étape correspondante ; celui de l’étape 07 y est entré le 14 août 2026.

## Étape 04, spike H5P critique

- [x] Protocole et paquet pilote validés.
- [x] Lecture H5P Standalone validée.
- [x] Événement xAPI réel validé.
- [x] Compatibilité et sécurité analysées.
- [x] ADR-012 acceptée sous conditions.
- [x] Étape 04 clôturée.

## Étape 05, UX design et navigation

- [x] Parcours Visiteur, Parent et Élève documentés.
- [x] Routes et règles de navigation documentées.
- [x] Bootstrap 5.3.8 adopté et Tailwind retiré.
- [x] Pages publiques et technique validées.
- [x] Layout et parcours Parent validés.
- [x] Layout et parcours Élève validés.
- [x] États transversaux et page introuvable validés.
- [x] Accessibilité et responsive validés manuellement.
- [x] TypeScript, ESLint et build Next.js validés.
- [x] Ruff, Mypy et 12 tests Pytest validés.
- [x] Rapport de validation de l’étape 05 produit.
- [x] Validation GitHub Actions et fusion vers `main`.
- [x] Étape 05 clôturée.

## Étape 06, backend identité et famille, clôturée

Travaux menés sur la branche `feat/backend-identity-family`, fusionnée dans `main`
le 14 août 2026 par la Pull Request #4, commit de fusion `a49ec43`.

### 06.1, modèles Parent et Enfant, validée localement

- [x] Modèles SQLAlchemy `Parent` et `Child`, relation familiale en cascade.
- [x] Migration `0002_identity_family_models`, réversible jusqu’à `base`.
- [x] Dérive entre modèles et migration corrigée sur `auth_parents.email` :
      l’unicité vient d’une `UniqueConstraint` nommée, l’index redondant a été
      retiré et `alembic check` est vert.
- [x] `alembic check` et le cycle downgrade puis upgrade ajoutés à l’API CI.
- [x] Validation indépendante rejouée localement le 14 août 2026 : `alembic check`
      vert, cycle downgrade base puis upgrade head rejoué, aucune dérive.
- [ ] Clôture distante.

### 06.2, authentification Parent et sessions, validée localement

- [x] Routes `POST /api/v1/auth/parent/register`, `POST /api/v1/auth/parent/login`,
      `DELETE /api/v1/auth/logout` et `GET /api/v1/auth/me`.
- [x] Mots de passe hachés en Argon2id, réponses identiques pour un mot de passe
      erroné et une adresse inconnue.
- [x] Sessions opaques en Redis, indexées par l’empreinte du jeton, cookie
      `HttpOnly` et `SameSite=lax`, révocation immédiate à la déconnexion.
- [x] Aucune table SQL de session, conformément à ADR-005.
- [x] Validation indépendante rejouée localement le 14 août 2026 : parcours complet
      sur l’API vivante, mot de passe erroné et adresse inconnue rendant une réponse
      identique, session Redis créée puis supprimée à la déconnexion.
- [ ] Clôture distante.

### 06.3, création et accès Enfant, validée localement

- [x] **Unicité du pseudonyme familiale et non globale**, sur décision du
      propriétaire : deux familles peuvent chacune avoir une `lea`, et le
      pseudonyme ne désigne plus personne à lui seul.
- [x] Code famille de six caractères frappé à l’inscription du Parent, rendu dans
      son profil public, alphabet sans caractères confondables à la lecture.
- [x] Régénération du code par le Parent, `POST /api/v1/auth/parent/family-code/regenerate` :
      l’ancien code cesse aussitôt de fonctionner, les sessions déjà ouvertes et
      les profils existants ne sont pas touchés.
- [x] Routes `POST /api/v1/auth/children`, `POST /api/v1/auth/child/register`,
      `GET /api/v1/auth/children`, `POST /api/v1/auth/children/{id}/activate`,
      `DELETE /api/v1/auth/children/{id}`, `POST /api/v1/auth/child/login` et
      `GET /api/v1/auth/child/me`.
- [x] Retrait d’une demande en attente par le Parent, complément de la
      régénération du code : le profil est supprimé et son pseudonyme redevient
      libre. Un profil actif répond `409`, son retrait relevant d’une décision à
      part entière.
- [x] Auto-inscription de l’Enfant par le code famille : le profil est créé en
      attente, ne peut pas ouvrir de session, et n’est utilisable qu’une fois
      activé par le Parent. Connaître un code permet de demander à rejoindre une
      famille, jamais d’y entrer.
- [x] Trois états de profil, `pending`, `active` et `disabled`, à la place du
      booléen `is_active`.
- [x] PIN de six chiffres haché en Argon2id, chiffre répété et suite continue
      refusés à la création.
- [x] Session Enfant `user_type=child` d’une journée au lieu de sept, socle de
      session et route de déconnexion réutilisés sans modification.
- [x] Verrou sur les tentatives de PIN, compteur d’échecs par enfant en Redis à
      fenêtre glissante, `429` au-delà du plafond y compris pour le bon PIN.
- [x] Isolation familiale portée par les requêtes : rattachement à la session ou
      au code famille, liste filtrée, activation limitée à sa propre famille avec
      un `404` indistinct, `403` croisé entre espace Parent et espace Enfant.
- [x] Migration `0003_family_code_child_status`, avec remplissage des codes famille
      existants et bascule du booléen vers le statut. Son retour arrière est
      réversible tant qu’aucun pseudonyme n’est partagé par deux familles ; sinon
      elle s’arrête avec un message plutôt que de renommer des profils.
- [x] Validation indépendante rejouée localement le 14 août 2026, consignée dans
      `rapport_2026-08-14_cloture_etape_06.md`.
- [ ] Clôture distante.

### 06.4, clôture de l’étape, terminée

- [x] Séquence complète de l’API CI rejouée localement, tout vert.
- [x] Rapport de validation `rapport_2026-08-14_cloture_etape_06.md` produit.
- [x] `PLANNING.md` complété par la phase 2 et les tâches BE-01 à BE-04.
- [x] Branche `feat/backend-identity-family` poussée, commits `ae97bd9`, `ff58ed0`,
      `da601ca` et la fusion `81da709`.
- [x] Pull Request #4 ouverte vers `main`.
- [x] Conflit avec `main` résolu : la PR #3 du 13 août avait fusionné une version
      antérieure des mêmes fichiers, ce qui empêchait GitHub de construire la
      fusion d’essai et donc de lancer le moindre contrôle. `main` a été fusionnée
      dans la branche ; l’arbre obtenu est identique à celui de la branche, `main`
      n’apportant rien qu’elle n’avait déjà.
- [x] API CI distante réussie sur la Pull Request, `test` en 1 min 40 s.
- [x] Secret Scan distant réussi sur la Pull Request, `Gitleaks` en 10 s.
- [x] Fusion vers `main` le 14 août 2026, commit `a49ec43`.
- [x] API CI et Secret Scan réussis sur `main` après la fusion, `test` en 1 min 42 s.
- [x] Étape 06 clôturée.

### Dette de l’étape 06, résorbée le 14 août 2026

Trois dettes consignées à la clôture ont été traitées après elle, sur la branche
`fix/step06-child-lifecycle`. Rapport :
`rapport_2026-08-14_1530_dette_etape_06.md`.

- [x] **Cycle de vie d’un profil Enfant.** Désactivation qui révoque sur-le-champ
      les sessions ouvertes, réactivation, réinitialisation du PIN par le Parent
      qui lève aussi le verrou, changement de PIN par l’Enfant contre le PIN
      actuel, et suppression d’un profil en attente ou désactivé. Un profil actif
      doit d’abord être désactivé pour être supprimé.
- [x] **Révocation en bloc des sessions d’un compte**, par un index Redis
      `user-sessions:<id>`, sans lequel un changement de PIN ne fermait rien.
- [x] **Retour arrière de la migration `0003`.** Il ne s’arrête plus : les
      pseudonymes partagés entre familles sont tranchés par une règle, le plus
      ancien garde le sien et les autres reçoivent un suffixe tiré de leur
      identifiant, chaque renommage étant journalisé en `WARNING`.
- [x] **ADR-005 amendée** : unicité familiale et code famille, Argon2id au lieu de
      bcrypt, plafond sur les tentatives de PIN, précisions sur les sessions
      Redis. Registre des décisions mis à jour.

### Points ouverts

Les stratégies de résolution sont décrites dans
`docs/backend/points-ouverts-authentification.md`.

- La vérification d’adresse email prévue par ADR-005 n’est pas implémentée faute
  de service d’envoi ; `is_verified` reste à `false` et la connexion ne l’exige pas.
- Aucune limitation de débit sur la connexion Parent, alors que `RATE_LIMIT` existe
  déjà sans être branché. La connexion Enfant fait exception depuis 06.3 : elle
  dispose d’un compteur d’échecs par enfant, qui protège un profil et non le service.
- Un profil Enfant ne se modifie pas : ni pseudonyme, ni nom affiché, ni date de
  naissance. Le changement de pseudonyme demandera de décider ce qu’il advient de
  l’historique attaché.
- Rien ne plafonne les profils en attente : qui connaît un code famille peut
  remplir la liste d’un Parent de profils `pending`, sans jamais obtenir d’accès.
  Le Parent peut régénérer son code et écarter ces demandes une à une, mais ni
  plafond ni notification n’existent encore.
- [x] `argon2-cffi` intégré aux images `api` et `worker` reconstruites.
- [x] `steps/MANIFESTE.md` régénéré depuis l’arborescence réelle, avec la règle
      d’inventaire et la commande de régénération.

## Résultats techniques de l’étape 06

```text
Alembic    : 0003_family_code_child_status (head), downgrade -1 puis base, retour au head validés
Alembic    : check vert, aucune dérive entre modèles et base
Ruff       : vert, format inclus, 50 fichiers
Mypy       : vert sur 23 fichiers
Pytest     : 141 tests réussis, dette de l’étape 06 comprise
API vivante: parent register 201 avec code famille, login 200 avec cookie durci, logout 204
API vivante: deux familles créent chacune une « lea » en 201, doublon interne refusé en 409
API vivante: child login 200 par code famille, code d’une autre famille et code inconnu en 401
API vivante: auto-inscription 201 en attente, connexion refusée 403, activation par le parent 200
API vivante: activation par une autre famille 404, cinq PIN erronés puis verrou 429
API vivante: régénération 200, ancien code 401 et 404, nouveau code 200, session ouverte intacte
API vivante: demande en attente écartée 204 et pseudonyme libéré, profil actif 409, inexistant 404
API vivante: désactivation 200 fermant les deux sessions ouvertes, suppression ensuite 204
API vivante: PIN réinitialisé 200 levant le verrou 429, PIN changé par l’enfant 200, session gardée
Alembic    : downgrade avec trois « lea » de familles différentes, deux renommées et journalisées
```

## Étape 07, référentiel de compétences, en cours

Travaux menés sur la branche `feat/referentiel-competences`.

### 07.1, référentiel scolaire, en revue

- [x] Trois décisions de conception tranchées par le propriétaire : quatre tables
      explicites plutôt qu’un arbre générique, versionnement porté par une entité
      version, arbre de prérequis modélisé dès maintenant.
- [x] Modèles `ReferentialVersion`, `Level`, `Subject`, `Domain`, `Competency` et
      `CompetencyPrerequisite`.
- [x] Étanchéité des versions portée par le schéma : chaque ligne fille répète le
      `version_id` de son parent et le référence par une clé étrangère composite,
      donc rien ne peut pointer d’une édition vers une autre.
- [x] Code métier stable, unique dans sa version et non au-delà.
- [x] Une seule version publiée à la fois, par index unique partiel.
- [x] Migration `0004_referential_competencies`, réversible, `alembic check` vert.
- [x] 23 tests dédiés, dont 16 vérifiant que les contraintes refusent réellement.
- [ ] Clôture distante.

### Points ouverts de l’étape 07

- [x] ADR-004 amendée le 14 août 2026 : son esquisse d’une table `skills` unique
      auto-référencée est remplacée par la description des quatre tables
      explicites et du versionnement. Le registre des décisions, qui affichait
      encore cette ADR comme « à créer », a été corrigé.
- La détection des cycles dans l’arbre de prérequis dépasse ce qu’une contrainte
  SQL exprime ; elle appartient à la validation d’import de 07.2.

## Dernier rapport appliqué

`steps/07_referentiel_competences/rapport_2026-08-14_1730_modeles_referentiel.md`.

## Historique de clôture de l’étape 06

- Pull Request #3 du 13 août : première coupe des modèles d’identité, fusionnée
  alors que la branche continuait d’évoluer.
- Pull Request #4 du 14 août : reste de l’étape 06. Elle est d’abord ressortie en
  conflit et sans aucun contrôle, GitHub ne lançant rien tant qu’il ne peut pas
  construire la fusion d’essai. `main` fusionnée dans la branche, conflits résolus
  du côté de la branche, qui portait déjà ce contenu et sa suite.
- Commit de fusion `a49ec43`, API CI et Secret Scan verts sur `main`.

## Prochaine action

Engager la sous-étape 07.2, import contrôlé et idempotent du référentiel.
