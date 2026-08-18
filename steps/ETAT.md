# État du projet

## Référence

- Projet : StudentConnect
- Date : 18 août 2026
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

**Les seize dossiers d’étape sont dans le dépôt**, et la règle antérieure — un
dossier rejoint le dépôt au démarrage de son étape — est abandonnée le 15 août
2026, à l’audit de cohérence.

Elle contredisait `MANIFESTE.md`, qui inventorie les quatre-vingt-douze fiches
avec leur empreinte SHA-256, celles des étapes non ouvertes comprises. Une
empreinte sert à détecter qu’une fiche a changé sans qu’on le dise ; une
empreinte portant sur un fichier absent du dépôt ne vérifie rien du tout. Les
deux règles ne pouvaient pas tenir ensemble, et c’est l’inventaire qui a une
utilité.

Les dossiers des étapes 12 à 16 avaient d’ailleurs été réintroduits sans
intention, par un `git add steps` trop large lors de la clôture de l’étape 08,
commit `fc1c103` — la même erreur que celle corrigée par la Pull Request #13.
Constater qu’une règle est enfreinte deux fois sans que personne s’en aperçoive
est aussi un argument contre elle.

Ce qui reste vrai : une fiche d’étape non ouverte est un **brouillon**. Elle
décrit ce qui est prévu, pas ce qui est décidé, et l’ouverture de l’étape la
réécrit souvent.

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
- [x] Clôture distante avec l’étape, Pull Request #4, commit `a49ec43`.

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
- [x] Clôture distante avec l’étape, Pull Request #4, commit `a49ec43`.

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
- [x] Clôture distante avec l’étape, Pull Request #4, commit `a49ec43`.

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

## Étape 07, référentiel de compétences, clôturée

Étape fusionnée dans `main` le 15 août 2026 par la Pull Request #14, commit de
fusion `9567240`. API CI et Secret Scan verts sur la Pull Request puis sur
`main`. Les sous-étapes 07.1 et 07.2 avaient été fusionnées séparément, par les
Pull Requests #9 et #11, avant la consigne du propriétaire de ne fusionner qu'à
la clôture d'une étape.

### 07.1, référentiel scolaire, clôturée

Travaux menés sur la branche `feat/referentiel-competences`, fusionnée dans
`main` le 14 août 2026 par la Pull Request #9. ADR-004 amendée ensuite par la
Pull Request #10, commit de fusion `71776c7`.

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
- [x] Clôture distante, Pull Requests #9 et #10 fusionnées.

### 07.2, import contrôlé, clôturée

Travaux menés sur la branche `feat/import-referentiel`, fusionnée dans `main` le
14 août 2026 par la Pull Request #11, commit de fusion `90b28e1`.

- [x] Deux décisions de conception tranchées par le propriétaire : l’idempotence
      est une réconciliation de brouillon, et l’import est une commande en ligne
      plutôt qu’une route d’administration.
- [x] Le fichier décrit **l’état voulu d’une édition** : l’import crée,
      met à jour et **supprime** ce que le fichier ne mentionne plus. Rejouer le
      même fichier ne rapporte rien à faire.
- [x] L’identité d’une ligne est son code métier : déplacer une compétence d’un
      domaine à un autre met à jour la ligne et lui conserve son identifiant.
- [x] Une version `published` ou `archived` est immuable, l’import la refuse et
      demande un nouveau code de version. Les traces des étapes 10 à 12 ne
      peuvent pas changer de sens rétroactivement.
- [x] Validation complète avant toute écriture, **toutes les erreurs rendues en
      une passe**, chacune nommant la ligne fautive du fichier.
- [x] **Détection des cycles de prérequis**, dette consignée par 07.1 : parcours
      en profondeur itératif, une même boucle signalée une seule fois. C’est la
      seule vérification sans équivalent en base.
- [x] Commande `python -m app.referential <fichier> [--apply]`, **essai à blanc
      par défaut**. L’essai fait le travail entier et l’annule, donc il éprouve
      réellement les contraintes au lieu de les estimer.
- [x] Codes de retour distincts : `1` illisible, `2` refusé, `3` immuable,
      `4` refus de la base.
- [x] Référentiel fictif livré, cinq niveaux, deux matières, huit domaines,
      trente-neuf compétences et trente-six prérequis traversant les niveaux.
- [x] Aucune migration : le schéma de 07.1 n’a pas bougé.
- [x] 54 tests dédiés, dont 22 d’intégration contre PostgreSQL réel.
- [x] Clôture distante : API CI et Secret Scan verts sur la Pull Request #11
      puis sur `main` après la fusion, `test` en 1 min 48 s.

### 07.3, API du référentiel, clôturée

Travaux menés sur la branche `feat/etape-07-referentiel`.

- [x] Deux décisions de conception tranchées par le propriétaire : toute session
      authentifiée peut lire, Parent comme Enfant, et les routes servent
      l’édition en vigueur et elle seule.
- [x] Commande `python -m app.referential publish <code>`, décidée à la fin de
      07.2 : le brouillon entre en vigueur et l’édition remplacée est archivée
      **dans la même transaction**, l’ancienne étant libérée avant que la
      nouvelle ne prenne sa place. Aucun instant à deux éditions publiées, aucun
      sans édition.
- [x] Republier une édition archivée est refusé : la ramener changerait le sens
      des traces enregistrées depuis son archivage.
- [x] Quatre routes sous `/api/v1/referential` : `edition`, `levels`, `subjects`
      et `competencies`. Sans session, `401`.
- [x] **Un brouillon ne sort jamais par HTTP.** Il se relit par la commande
      d’import en essai à blanc, par qui a accès au serveur.
- [x] **Chaque réponse nomme l’édition qu’elle a lue**, et `edition` vaut `null`
      quand rien n’est publié, ce qui n’est pas une erreur.
- [x] Codes métier exposés, jamais les UUID, refrappés à chaque import.
- [x] Filtres `level`, `subject` et `domain` combinables ; un code inconnu rend
      une page vide et non une erreur.
- [x] Pagination plafonnée à 100, bornes refusées en `422`, **ordre total** pour
      qu’aucune ligne ne soit vue deux fois ni jamais.
- [x] Arbre de prérequis non exposé, il appartient à l’étape 12.
- [x] Fragilité des tests de 07.1 et 07.2 corrigée : quatre tests publiaient une
      édition en supposant qu’aucune ne l’était, ce qui échouait en local sans
      jamais échouer en CI. `tests/support.py` les fait écarter l’édition en
      place puis la remettre.
- [x] Aucune migration : le schéma de 07.1 n’a pas bougé.
- [x] 37 tests dédiés, tous d’intégration contre PostgreSQL réel.
- [x] Clôture distante, avec l’étape entière.

### 07.4, clôture de l’étape, terminée

- [x] Séquence complète de l’API CI rejouée localement, tout vert, 255 tests.
- [x] Rapport d’étape `rapport_2026-08-15_1440_cloture_etape_07.md` produit.
- [x] **Une seule Pull Request pour toute l’étape**, sur consigne du
      propriétaire du 15 août 2026 : la fusion vers `main` n’a lieu qu’à la
      clôture de la grande étape. Les sous-étapes 07.1 et 07.2 avaient été
      fusionnées séparément avant cette consigne.
- [x] Trois corrections menées en cours d’étape : ADR-004 amendée, garde-fou
      posé sur les déclarations `overlaps`, et quatre tests qui publiaient une
      édition en supposant qu’aucune ne l’était — ils échouaient en local en
      passant en CI, ce qui est le pire des deux cas.

### Points ouverts de l’étape 07

- [x] ADR-004 amendée le 14 août 2026 : son esquisse d’une table `skills` unique
      auto-référencée est remplacée par la description des quatre tables
      explicites et du versionnement. Le registre des décisions, qui affichait
      encore cette ADR comme « à créer », a été corrigé.
- [x] La détection des cycles dans l’arbre de prérequis, hors de portée d’une
      contrainte SQL, a été livrée avec la validation d’import de 07.2.
- **Rien ne permet encore de publier une édition.** L’import s’arrête au
  brouillon, et mettre une version en vigueur est un acte distinct dont la
  décision revient au propriétaire. Tant qu’il n’existe pas, les lectures de
  07.3 n’auront aucune édition publiée à servir : c’est le premier point à
  trancher en ouvrant 07.3.
- Aucune comparaison entre deux éditions. Le code métier stable la rendra
  possible ; rien ne la demande encore.
- [x] Les déclarations `overlaps` des quatre relations qui partagent `version_id`
      ne reposent plus sur la vigilance : un test configure les mappers avec les
      avertissements de SQLAlchemy transformés en erreurs, dans un sous-processus.
      Vérifié en les retirant toutes, le test échoue.
- [x] La publication d’une édition, tranchée par le propriétaire, a été livrée
      avec 07.3.
- Aucune lecture d’une édition archivée. Les traces des étapes 10 à 12 devront
  être relues dans le référentiel où elles ont été écrites ; il faudra alors
  décider qui peut lire une édition retirée.
- La publication n’est journalisée que par la sortie de la commande. Savoir qui
  a publié quoi et quand relèvera de l’étape 15.

## Résultats techniques de l’étape 07

```text
Ruff       : vert, format inclus
Mypy       : vert sur 32 fichiers
Alembic    : 0004_referential_competencies (head), check vert, downgrade base et retour au head
Pytest     : 255 tests réussis, dont 114 dédiés au référentiel
Référentiel: 23 tests de contraintes, 54 pour l’import, 37 pour la publication et les routes
Commande   : essai à blanc, 5 niveaux, 2 matières, 8 domaines, 39 compétences, 36 prérequis
Commande   : essai à blanc annulé, version absente de la base
Commande   : --apply, version créée en brouillon, base comptée à 5 / 2 / 8 / 39 / 36
Commande   : rejoué, 0 création, 0 modification, 0 suppression
Commande   : fichier fautif refusé, 3 erreurs nommant leur ligne, code de retour 2
Commande   : version publiée puis archivée refusées, code de retour 3, édition intacte
Commande   : fichier absent, code de retour 1 ; JSON malformé, code de retour 2
Tests      : cycle à deux et à trois compétences détecté, losange non confondu avec un cycle
Tests      : compétence déplacée de domaine, même identifiant conservé
Commande   : publish sur un brouillon, mise en vigueur ; rejoué, « déjà en vigueur »
Commande   : publish sur un code inconnu, code de retour 3
API vivante: sans session, 401 sur les quatre routes de lecture
API vivante: /edition rend l’édition en vigueur, /levels les cinq niveaux en ordre
API vivante: /competencies?level=cm1&subject=math&page_size=2 rend 2 items, total 5
Tests      : l’édition remplacée est archivée, exactement une reste en vigueur
Tests      : un brouillon n’est jamais servi, aucune réponse ne contient de prérequis
Tests      : trois pages de deux rendent cinq compétences distinctes
```

## Dernier rapport appliqué

`steps/13_dashboards/rapport_2026-08-16_2200_dashboards.md`.

## Historique de clôture de l’étape 06

- Pull Request #3 du 13 août : première coupe des modèles d’identité, fusionnée
  alors que la branche continuait d’évoluer.
- Pull Request #4 du 14 août : reste de l’étape 06. Elle est d’abord ressortie en
  conflit et sans aucun contrôle, GitHub ne lançant rien tant qu’il ne peut pas
  construire la fusion d’essai. `main` fusionnée dans la branche, conflits résolus
  du côté de la branche, qui portait déjà ce contenu et sa suite.
- Commit de fusion `a49ec43`, API CI et Secret Scan verts sur `main`.

## Étape 08, catalogue de contenus et activités, clôturée

Travaux menés sur la branche `feat/etape-08-catalogue`. Le propriétaire ayant
demandé d'enchaîner les sous-étapes sans arrêt, la décision structurante de
l'étape a été prise par l'agent et **reste à confirmer**.

### 08.1, modèle du catalogue, terminée

- [x] **ADR-013, décidée par l'agent et à confirmer** : le catalogue pointe vers
      les compétences **par leur code métier, sans clé étrangère**. Le référentiel
      est versionné parce que des traces le désignent ; le catalogue est un
      travail éditorial qui doit suivre le programme sans être reconstruit à
      chaque édition. La contrepartie, un lien que la base ne peut pas vérifier,
      est payée par une commande dédiée.
- [x] `catalog_activities`, `catalog_activity_competencies`,
      `catalog_h5p_packages`, migration `0005_catalog_activities` réversible.
- [x] La bibliothèque H5P est bornée par un `CHECK` à ce qu'autorise ADR-012 :
      admettre un second type demande une migration et un amendement d'ADR.
- [x] Durée bornée entre une et soixante minutes, un Quick Repair durant trois à
      sept minutes.
- [x] 27 tests de contraintes.

### 08.2, contenus H5P autorisés, terminée

- [x] Ni éditeur ni route de téléversement, par ADR-006 et ADR-012 : un paquet
      est vérifié, stocké et enregistré par quelqu'un qui a accès au serveur.
- [x] **L'archive est lue sans jamais être extraite.** Rien n'est écrit sur le
      disque, donc un nom d'entrée forgé n'a nulle part où s'échapper.
- [x] Refus des chemins remontants et absolus, des archives de plus de cinq cents
      entrées, des bombes de décompression, des fichiers au-delà de vingt
      mégaoctets.
- [x] Type refusé **avant que le moindre octet n'atteigne le bucket**. Vérification,
      stockage, écriture ; si l'écriture échoue, l'objet est retiré.
- [x] Empreinte calculée sur les octets lus, nommant l'objet dans le bucket.
- [x] Paquet pilote enregistré à la main : empreinte identique à celle publiée
      par ADR-012.
- [x] `python -m app.catalog check`, contrepartie d'ADR-013, qui nomme les liens
      morts et les activités reliées à rien.
- [x] 31 tests.

### 08.3, API du catalogue, terminée

- [x] `GET /api/v1/catalog/activities`, `.../{code}` et `/kinds`.
- [x] **Seules les activités publiées sont servies** ; un brouillon répond comme
      une activité inexistante.
- [x] Toute session authentifiée peut lire, Parent comme Enfant, comme en 07.3.
- [x] Filtres `competency`, `kind` et `max_duration` combinables, ordre total.
- [x] **Aucune réponse ne dit où vit un paquet** : clé d'objet, empreinte, licence
      et provenance restent côté serveur.
- [x] 23 tests.

### Dettes corrigées pendant l'étape 08

- [x] Le registre des décisions annonçait dix ADR dont neuf « à créer », alors
      que treize existaient. Reconstruit depuis les fichiers d'ADR.
- [x] Un test portait un nom plus fort que ce qu'il prouvait, la compensation du
      stockage n'étant jamais exercée.
- [x] Deux tests supposaient une base vide et une empreinte libre.

### Points ouverts de l'étape 08

- [x] **ADR-013 confirmée par le propriétaire** le 15 août 2026, après coup.
- Aucun antivirus dans le contrôle des paquets, exigé par ADR-012 pour la
  production ; aucun scanner disponible dans l'environnement de stage.
- Aucune remise de paquet au navigateur : origine de contenu isolée, CSP et
  endpoint xAPI authentifié restent à construire.
- Aucun import de masse du catalogue, contrairement au référentiel.

### 08.4, clôture de l'étape, terminée

- [x] Séquence complète de l'API CI rejouée localement, tout vert, 336 tests.
- [x] Rapports `rapport_2026-08-15_1530_catalogue.md` et
      `rapport_2026-08-15_1545_cloture_etape_08.md` produits.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #15 fusionnée le 15 août 2026, commit de
      fusion `b41284b`, API CI et Secret Scan verts sur la Pull Request puis sur
      `main`.

## Résultats techniques de l'étape 08

```text
Ruff       : vert, format inclus
Mypy       : vert sur 41 fichiers
Alembic    : 0005_catalog_activities (head), check vert, downgrade base et retour au head
Pytest     : 336 tests réussis, dont 81 dédiés au catalogue
Catalogue  : 27 tests de contraintes, 31 sur les paquets, 23 sur les routes
Commande   : paquet pilote enregistré, empreinte identique à celle publiée par ADR-012
Commande   : check, catalogue cohérent avec l'édition en vigueur, code de retour 0
Tests      : zip slip, chemin absolu, 501 entrées et bombe de décompression refusés
Tests      : quatre autres types H5P refusés, en code et par contrainte en base
Tests      : brouillon et archive répondant 404 comme une activité inexistante
Tests      : aucune réponse ne contient de clé d'objet, d'empreinte ni de licence
```

## Étape 09, affectations et parcours, clôturée

Travaux menés sur la branche `feat/etape-09-affectations`. Sous-étapes enchaînées
sans arrêt, sur consigne du propriétaire ; les décisions prises par l'agent sont
consignées ci-dessous.

### 09.1, modèle des affectations, terminée

- [x] Table `assignments`, migration `0006_assignments` réversible.
- [x] **Redonner une activité crée une seconde ligne**, décision de l'agent :
      « elle l'a faite deux fois » et « elle l'a faite une fois » sont deux faits
      différents. Un index unique **partiel**, sur les seuls états ouverts,
      interdit le doublon simultané sans interdire la répétition.
- [x] **Une activité affectée ne peut plus être supprimée** : la clé étrangère
      restreint au lieu de cascader, sans quoi les tentatives de l'étape 10
      pointeraient vers rien.
- [x] Trois contraintes exigent qu'un statut porte sa date.

### 09.2, API Parent, terminée

- [x] `POST /api/v1/assignments`, `GET /api/v1/assignments`,
      `POST /api/v1/assignments/{id}/cancel`.
- [x] **Annuler n'efface pas**, décision de l'agent : la ligne reste, datée. Un
      enfant à qui l'on a donné puis retiré quelque chose n'a pas la même
      histoire qu'un enfant à qui l'on n'a rien donné.
- [x] Une activité en brouillon est refusée comme une activité inexistante.
- [x] Isolation portée par la clause `WHERE`, comme à l'étape 06 : l'affectation
      d'une autre famille répond comme une affectation qui n'existe pas.

### 09.3, API Élève, terminée

- [x] `GET /api/v1/me/activities`, `.../start`, `.../complete`.
- [x] **Terminer n'est pas réussir**, décision de l'agent : rien ne touche à une
      compétence, conformément à la règle selon laquelle ouvrir un contenu ne
      valide jamais une compétence à lui seul. La preuve appartient à l'étape 10.
- [x] **Rien ne revient en arrière** : une affectation terminée ne se rouvre pas,
      une annulée ne reprend pas, `409` dans les deux cas.
- [x] **Les deux espaces ne se mélangent pas** : une route Parent exige
      `CurrentParent`, une route Élève exige `CurrentChild`. Un enfant ne peut
      pas se donner du travail, un parent ne peut pas terminer à sa place.
- [x] La vue Élève ne répète pas de quel enfant il s'agit : tout ce qu'elle
      montre est à lui.

### 09.4, clôture de l'étape, terminée

- [x] Séquence complète de l'API CI rejouée localement, tout vert, 361 tests.
- [x] Rapport `rapport_2026-08-15_1615_affectations.md` produit.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #16 fusionnée le 15 août 2026, commit de
      fusion `71af66e`. Dette résorbée ensuite par la Pull Request #17, commit
      `5bf1df0`, contrôles verts sur les deux.

### Dette de l'étape 09, résorbée le 15 août 2026

Les trois points ouverts à la clôture ont été traités après elle, sur la branche
`fix/dette-affectations-et-lecteur`.

- [x] **Échéance et ordre de parcours.** Une affectation porte une date
      facultative — une date et non un moment, la semaine d'un enfant se comptant
      en jours. Une échéance déjà passée est refusée. L'ordre en découle : ce qui
      est attendu le plus tôt d'abord, ce qui n'est attendu aucun jour ensuite.
      Le réordonnancement manuel a été écarté : il demanderait un rang à
      maintenir, et un rang que personne ne met à jour est pire que pas de rang.
- [x] **Plafond de vingt activités dues à la fois.** Il compte ce qui est encore
      dû, jamais ce qui a été donné : terminer ou annuler libère une place. Il
      n'est pas là contre un abus mais contre un geste, dont la conséquence
      serait d'ensevelir un enfant de six ans.
- [x] **Ouverture du contenu**, `GET /api/v1/me/activities/{id}/content` : lien
      signé de cinq minutes vers le paquet. **L'accès n'est pas une propriété du
      contenu mais de l'affectation** — rien avant d'avoir commencé, rien après
      avoir terminé, rien pour un autre enfant, rien pour le Parent. Le bucket
      reste privé : sans signature, le stockage répond `403`.
- [x] Migration `0007_assignment_due_date`, réversible.
- [x] 14 tests supplémentaires, 375 au total.

### Ce qui reste pour jouer réellement un contenu

Le lien remet le fichier vérifié ; il ne le **joue** pas. Aucune des trois pièces
manquantes n'est une ligne de code de plus dans l'API :

- **l'origine de contenu isolée**, sa CSP et son iframe, exigées par ADR-012
  condition 5 — servir le contenu depuis l'origine de l'API serait précisément ce
  que cette isolation interdit, c'est un travail d'infrastructure ;
- **le lecteur `h5p-standalone` dans le web**, qui suppose les bibliothèques
  préparées hors ligne et figées comme artefacts internes, condition 3 ;
- **l'endpoint xAPI authentifié**, condition 6, qui relève de l'étape 11 par
  construction.

Les pages web restent les maquettes de l'étape 05.

## Résultats techniques de l'étape 09

```text
Ruff       : vert, format inclus
Mypy       : vert sur 46 fichiers
Alembic    : 0006_assignments (head), check vert, downgrade base et retour au head
Pytest     : 361 tests réussis, dont 25 dédiés aux affectations
Tests      : affectation d'une autre famille refusée en 404, comme une inexistante
Tests      : enfant s'affectant une activité 403, parent terminant à sa place 403
Tests      : même activité due deux fois à la fois 409, redonnée après achèvement 201
Tests      : terminer avant de commencer, rouvrir, reprendre, annuler une terminée : 409
Tests      : annulation conservant la ligne et sa date
```

## Prérequis transverse, runtime de contenu, terminé

Travaux menés sur la branche `feat/etape-11-runtime-xapi`, fusionnés avant les
étapes 10 et 11 dont il est le prérequis commun.

### Un trou du découpage initial

Trois étapes présupposent un **runtime de contenu** sans qu'aucune ne le
construise : 11.2 parle de « ne pas exposer l'identité au runtime de contenu »,
13.1 d'une « activité à reprendre », et 16.1 teste les activités de bout en bout.
Le propriétaire a validé le 15 août 2026 de construire ce runtime avant les
étapes qui le présupposent : l'endpoint xAPI de 11.1 n'a aucun producteur tant
que rien ne joue de contenu, et une tentative de l'étape 10 n'a pas davantage de
sens sans contenu jouable.

### Une erreur d'ordre, corrigée le 15 août 2026

Ce travail avait d'abord été rattaché à l'étape 11, **avec un décalage de
l'étape 10 après elle**. Ce décalage était une erreur, et il n'avait pas été
soumis au propriétaire : l'objectif de 11.3 est de produire des agrégats « à
partir des événements **et résultats** », et ces résultats sont ceux de 10.3.
**L'étape 11 dépend de l'étape 10, pas l'inverse.**

Le raisonnement initial — une tentative n'a de sens qu'une fois un contenu
jouable — justifiait de faire le runtime en premier, pas d'inverser deux étapes.
Une conclusion valide avait été étendue au-delà de sa portée.

L'ordre du découpage initial est rétabli. Le runtime, lui, n'est le contenu
d'aucune des deux étapes : c'est leur **prérequis commun**, fusionné avant elles,
écart assumé à la règle d'une seule fusion par étape et validé par le
propriétaire.

### Ce que le runtime apporte

- [x] **Une seconde origine, servie par nginx.** Un contenu H5P est du
      JavaScript tiers qui a besoin d'`eval` et de scripts en ligne pour
      fonctionner. Le servir depuis l'origine de l'application lui donnerait
      accès aux cookies de session, et aucune CSP ne rattrape cela puisque le
      navigateur le considérerait comme faisant partie du site. **La séparation
      est la mesure elle-même**, et c'est aussi ce qui rend acceptables les
      `unsafe-inline` et `unsafe-eval` de sa CSP : ils ne coûtent rien là où il
      n'y a rien à prendre.
- [x] **Un ticket remplace le cookie**, qui ne voyage pas jusqu'à l'autre
      origine. Valeur opaque frappée quand un enfant ouvre une activité en
      cours, gardée trente minutes dans Redis, vérifiée par `auth_request` à
      chaque fichier. Il ne porte aucune identité : il nomme une affectation et
      le contenu qu'il ouvre. Rangé sous son empreinte comme une session, donc
      qui lit Redis apprend quels contenus sont ouverts, jamais les tickets.
- [x] Un ticket pour un autre contenu est refusé comme un ticket absent.
- [x] **Le déploiement est l'endroit où l'archive est enfin ouverte**, après
      avoir été vérifiée en 08.2. Elle est relue depuis le bucket, jamais depuis
      une copie sur disque, et les contrôles de chemin sont rejoués à l'écriture
      — non par méfiance envers le premier contrôle, mais envers l'intervalle
      entre les deux.
- [x] L'empreinte nomme le dossier : redéployer est idempotent, deux paquets ne
      peuvent pas se télescoper. Volume monté **en lecture seule** dans
      l'origine.
- [x] Inventaire des empreintes des bibliothèques, condition 3 d'ADR-012 : un
      artefact que personne ne peut nommer n'est pas figé.
- [x] `play.html`, seule partie de cette origine que nous ayons écrite, remonte
      les événements xAPI par `postMessage` sans jamais parler à l'API.
- [x] 23 tests dédiés, 397 au total. Éprouvé sur la pile vivante.

## Étape 10, tentatives et résultats, clôturée

Travaux menés sur la branche `feat/etape-10-tentatives`. Sous-étapes enchaînées
sans arrêt ; les décisions prises par l'agent sont consignées ci-dessous.

### La ligne qui structure l'étape

Les **faits** d'un côté, la **lecture** de l'autre, portés par des tables
distinctes plutôt que par une convention. Une tentative et une réponse sont des
faits ; un résultat est une interprétation, rangé à part parce qu'il en est une.
C'est ce qui rend applicables, plutôt que simplement énoncées, deux règles du
projet : une note ne remplace jamais une compétence, et une lacune automatique
est une candidate explicable.

### 10.1, modèle, terminée

- [x] `attempts`, `attempt_responses`, `attempt_results`, migration
      `0008_attempts` réversible.
- [x] **Aucune colonne de score, nulle part.** Un résultat porte trois mots et
      les comptes dont ils viennent.
- [x] Les réponses ne portent **aucune clé unique sur la question** : répondre
      deux fois est deux faits, et le second n'efface pas le premier.

### 10.2, API des tentatives, terminée

- [x] **Commencer est idempotent, et c'est la base qui le garantit** : un index
      unique partiel n'admet qu'une tentative en cours par affectation, donc deux
      requêtes simultanées ne peuvent pas gagner toutes les deux. Le perdant est
      renseigné sur le gagnant au lieu d'échouer.
- [x] `201` à la création, `200` à la reprise, sans qu'aucune soit une erreur.
- [x] Terminer la tentative termine l'affectation : les deux ne doivent pas
      pouvoir se contredire sur le fait que le travail a été fait.
- [x] Annuler une affectation abandonne la tentative **sans l'effacer** :
      l'enfant avait bien commencé, et cela reste vrai.

### 10.3, calcul des résultats, terminée

- [x] Trois règles nommées — `all-correct`, `majority-correct`,
      `too-few-correct` — de l'arithmétique sur des comptes, sans modèle opaque.
- [x] La maîtrise exige **tout** : réussir la plupart d'un exercice de trois
      questions n'est pas le maîtriser. La bande intermédiaire existe pour que
      « presque » ne soit pas rangé avec « pas du tout ».
- [x] Phrase explicative rendue par l'API, construite à partir des mêmes valeurs
      que celles stockées : elle ne peut pas diverger de ce qu'elle explique.
- [x] **Aucune preuve ne conclut rien.** Un contenu qui ne juge pas une réponse
      n'y est pas contraint ; si rien n'a été évalué, aucun résultat n'est écrit.
      Il n'existe volontairement pas de statut pour cela : ranger un silence sous
      « non acquise » en ferait une accusation.

### 10.4, clôture, terminée

- [x] Séquence complète de l'API CI rejouée localement, tout vert, 434 tests.
- [x] Rapport `rapport_2026-08-15_1820_tentatives.md` produit.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #19 fusionnée le 15 août 2026, commit de
      fusion `60b474b`, API CI et Secret Scan verts sur la Pull Request puis sur
      `main`. Dette résorbée ensuite par la Pull Request #20, commit `26d0ae1`,
      contrôles verts sur les deux.

### Deux défauts trouvés pendant l'étape 10

- [x] Les résultats n'apparaissaient pas dans la réponse : ils étaient écrits,
      mais la collection de la tentative avait été chargée vide avant leur
      création. Ils sont rattachés par la relation et non par une clé étrangère
      posée derrière son dos.
- [x] Deux tests supposaient qu'aucune autre activité ne citait la même
      compétence. Les codes de compétence des tests sont désormais tirés par
      exécution. C'est la troisième occurrence de cette famille de fragilité,
      traitée à la racine cette fois.

### Dette de l'étape 10, résorbée le 15 août 2026

Traitée après la clôture, sur la branche `fix/dette-etape-10`, migration
`0009_question_attribution` réversible.

- [x] **Attribution par question.** Une activité peut associer ses questions à
      des compétences ; chaque question ne compte alors que pour ce qu'elle
      travaille, et une compétence sans question à elle ne reçoit **aucun**
      résultat plutôt qu'un résultat emprunté. Rien dans un paquet H5P ne dit
      cette association : elle est déclarée par qui enregistre l'activité.
      Sans elle, l'ancien comportement demeure — la plateforme ne peut pas en
      dire plus que l'activité — et c'est écrit plutôt que caché.
- [x] **Provenance des réponses.** Chaque réponse porte `declared` ou `xapi`.
      **Le champ n'est pas dans la charge utile** : un client capable de déclarer
      « ceci vient du runtime » annulerait la distinction, et une charge utile
      qui le mentionne est refusée. Enregistrer laquelle est laquelle dès
      maintenant permettra à l'étape 11 de trancher sans deviner pour les lignes
      déjà écrites. `recorded_at` reste l'horloge du serveur, comme ADR-012 le
      demande.
- [x] **Seuils publiés plutôt que configurables**, `GET /api/v1/attempts/rules`.
      Les rendre réglables reviendrait à décider qui peut changer ce que
      « acquise » veut dire : c'est une décision, pas un réglage, et personne ne
      peut la prendre avant le rôle Administrateur de l'étape 15. Publier donne
      la même transparence sans inventer une autorité.
- [x] 6 tests supplémentaires, 440 au total.

### Points ouverts de l'étape 10

- Les réponses restent **déclarées par le client**, ce que leur provenance dit
  désormais explicitement. L'étape 11 apportera celles du runtime, et il faudra
  décider ce qui prime.
- Aucun agrégat dans le temps : un résultat porte sur une tentative.

## Résultats techniques de l'étape 10

```text
Ruff       : vert, format inclus
Mypy       : vert sur 56 fichiers
Alembic    : 0009_question_attribution (head), check vert, downgrade base et retour au head
Pytest     : 441 tests réussis, dont 42 dédiés aux tentatives
Tests      : dix demandes de démarrage laissent une seule tentative
Tests      : deux réponses à la même question conservées, la dernière lue
Tests      : aucune réponse évaluée, aucun résultat écrit
Tests      : chaque résultat nomme sa règle et porte ses comptes
Tests      : aucun résultat ne porte de score ni de pourcentage
Tests      : annuler l'affectation abandonne la tentative sans l'effacer
```

## Audit de cohérence du 15 août 2026

Audit transversal demandé par le propriétaire avant d'ouvrir l'étape 11 : code,
documentation, ADR, registre, fiches et état du dépôt relus les uns contre les
autres. Huit incohérences trouvées, toutes corrigées.

### Un contrôle qui ne disait pas la même chose selon l'endroit

- [x] **`mypy` n'était pas vert en local**, contrairement à ce que ce fichier
      affirmait. Le `--ignore-missing-imports` n'existait que dans le workflow
      d'API CI : `mypy app` lancé à la main rendait deux erreurs que la CI ne
      montrait jamais. La configuration est passée dans `pyproject.toml` et le
      workflow appelle désormais `mypy app` tout court, si bien que la commande
      d'un développeur et celle de la CI ne peuvent plus diverger.
      `celery` et `boto3` y sont nommés un par un plutôt que d'ignorer tout
      import manquant : la prochaine dépendance sans stubs sera signalée au lieu
      d'être avalée en silence.

      C'est la quatrième fois sur ce projet qu'un contrôle passe d'un côté et
      échoue de l'autre. Les trois précédentes venaient de tests qui
      présupposaient une base vide ; celle-ci vient d'un réglage écrit à un seul
      des deux endroits qui l'exécutent.

### Un défaut de conception, et non de rédaction

- [x] **`GET /api/v1/attempts/rules` n'était lisible que par l'Élève.** Les
      règles sont publiées précisément pour qu'un parent puisse se les voir
      montrer — c'est la raison écrite dans le code même. Derrière une porte que
      seul un enfant ouvre, elles étaient publiées à personne qui en a besoin.
      La route accepte désormais toute session authentifiée, comme les lectures
      du référentiel et du catalogue. Les quatre routes qui touchent réellement à
      une tentative restent réservées à `CurrentChild`.

### Cinq documents qui décrivaient un état révolu

- [x] **`attempts/rules.py`** affirmait encore que la lecture vaut pour toutes
      les compétences « parce que H5P ne dit pas quelle question appartient à
      quelle compétence » — ce que l'attribution par question avait démenti la
      veille. Le fichier ne prétend plus décider à quoi un compte se rapporte :
      cette question appartient au service, et le dire ainsi empêche l'écart de
      se reformer.
- [x] **`catalogue-activites.md`** annonçait « trois tables » depuis que
      `catalog_activity_questions` en faisait quatre. La table y est maintenant
      décrite, avec la raison de sa facultativité.
- [x] **`affectations.md`** omettait deux routes livrées avec la dette de
      l'étape 09, dont l'ouverture du contenu.
- [x] **Le registre des décisions** se disait « en construction » au 10 août et
      affichait un arbre où onze ADR restaient « à créer », alors que sa propre
      liste en détaille quatorze et que les quatorze fichiers existent. Il
      renvoyait aussi vers un dossier de diagrammes et un template inexistants.
- [x] **`ETAT.md`** portait la date du 13 août, trois sous-étapes de l'étape 06
      encore en attente de clôture distante alors que l'étape est fusionnée
      depuis le 14, l'étape 07.3 « en revue » dans une étape clôturée, et le
      rapport de l'étape 07 comme dernier rapport appliqué.

### ADR-012 acceptée sous conditions, sans suivi de ses conditions

- [x] Ses huit conditions n'étaient suivies nulle part, et ses conséquences
      exigeaient encore une isolation livrée par `PRE-01`. Une ADR acceptée sous
      conditions dont personne ne suit les conditions n'est plus qu'une ADR
      acceptée. Un tableau de suivi y figure désormais : cinq conditions
      remplies, deux partielles — l'antivirus et la vérification de licence —,
      une entière à faire, l'endpoint xAPI de l'étape 11.

### La clôture distante de l'étape 10, à consigner

- [x] Consignée : Pull Requests #19 et #20, commits `60b474b` et `26d0ae1`.

## Étape 11, événements xAPI et progrès, clôturée

Travaux menés sur la branche `feat/etape-11-xapi`. Sous-étapes enchaînées sans
arrêt ; les décisions prises par l'agent sont consignées dans ADR-014 et
rappelées ci-dessous.

### La question à laquelle l'étape répond

Un contenu jouait, émettait des événements, et personne ne les recevait. La
difficulté n'était pas d'ouvrir une route : c'était de dire **qui a le droit
d'envoyer un événement**, **quel acteur écrire** quand le runtime à qui l'on ne
dit rien en revendique un, et **qui a raison** quand le navigateur et le runtime
décrivent la même question. Ces trois questions ne se répondent pas séparément.

### 11.1, ingestion et validation, terminée

- [x] Table `xapi_statements`, migration `0010_xapi_statements` réversible.
- [x] `POST /api/v1/me/xapi/statements` exige **deux choses à la fois** : la
      session Élève et le ticket de contenu, dans un en-tête. Le ticket n'est pas
      une partie de l'événement, et un événement qui porterait sa propre
      autorisation serait à une falsification près d'être sa propre permission.
- [x] **Le client ne nomme jamais la tentative** : le serveur la déduit du
      ticket. Un client capable de la désigner pourrait déposer une observation
      sur un autre travail.
- [x] La validation **refuse plutôt qu'elle ne répare**. Un identifiant d'objet
      trop long est rejeté et non tronqué : raccourcir fusionnerait deux
      questions en une.
- [x] Un rejeu est reconnu, pas recompté : `(attempt_id, statement_id)` unique,
      et l'unicité est portée par la tentative plutôt que globale, sinon une
      famille pourrait faire taire l'événement d'une autre en réservant son
      identifiant la première.
- [x] Seul `answered` devient une réponse ; les sept autres verbes sont
      conservés et ne concluent rien. Un événement ne termine pas la tentative :
      terminer est un acte délibéré, une observation n'en est pas un.

### 11.2, liaison de l'acteur pseudonyme, terminée

- [x] **L'acteur revendiqué est jeté**, remplacé par
      `HMAC-SHA256(SECRET_KEY, "xapi-actor:" + identifiant de l'enfant)`. Le
      runtime ne reçoit aucune identité, donc rien de ce qu'il nomme là n'en est
      une que nous lui ayons donnée ; conserver le champ laisserait un navigateur
      écrire un vrai nom dans la base par un champ que personne ne lit.
- [x] La clé est dérivée avec le secret pour qu'une copie de la base ne se lise
      pas comme une liste d'enfants. Faire tourner le secret ne casse rien : le
      lien à l'enfant est la clé étrangère, jamais ce nom.
- [x] Dans l'autre sens, l'URL de lecture ne porte ni identifiant d'enfant, ni
      pseudonyme, ni code famille, ni affectation. C'était vrai depuis `PRE-01` ;
      c'est désormais **éprouvé par un test**, parce qu'une propriété d'isolation
      que personne ne vérifie finit par ne plus être vraie.

### 11.3, agrégation des progrès, terminée

- [x] `GET /api/v1/me/progress` et `GET /api/v1/children/{child_id}/progress`.
      Deux routes pour une lecture, plutôt qu'une route à identifiant facultatif
      qui serait à un contrôle oublié près de montrer à une famille le travail
      d'une autre.
- [x] **Aucune table d'agrégats.** Le calcul se fait à chaque lecture : c'est ce
      qui rend les agrégats reproductibles au sens demandé, et il n'existe pas
      une quatrième chose capable de contredire les trois dont elle est tirée.
- [x] **Les résultats sont sommés, jamais recalculés.** Recalculer appliquerait
      l'attribution question-compétence d'aujourd'hui aux réponses d'hier et
      changerait sans le dire une conclusion déjà montrée à un parent.
- [x] Le dernier mot plutôt qu'une moyenne, les comptes cumulés, une phrase en
      français, et **aucun ratio ni score nulle part** — vérifié sur la charge
      utile elle-même.
- [x] Un bloc `evidence` dit sur quoi la lecture repose : c'est ce qui fait de
      cette agrégation une agrégation des événements **et** des résultats.
- [x] Rien n'y diagnostique : c'est l'étape 12, et en poser une première version
      ici ferait décider à deux endroits ce qu'est une difficulté.

### La décision que l'étape 10 avait laissée ouverte

- [x] **Un événement du runtime prime sur une réponse déclarée**, quel que soit
      l'ordre d'arrivée ; entre deux sources de même nature, la plus récente
      l'emporte toujours. Ce n'est pas que l'un serait plus dur à falsifier — les
      deux passent par le même navigateur — mais que ce sont deux récits d'un
      même fait, et que celui que le serveur a lui-même interprété est celui
      qu'il garde. L'ordre inverse laisserait un client défaire un événement du
      runtime en publiant sa propre déclaration juste après. Les deux lignes
      restent en base : l'une n'est pas lue, aucune n'est effacée.

### 11.4, clôture, terminée

- [x] Séquence complète de l'API CI rejouée dans le conteneur `api`, tout vert,
      499 tests, dont 58 pour cette étape.
- [x] Suite complète rejouée **deux fois** : sur le schéma courant, puis sur un
      schéma reconstruit depuis `base`.
- [x] Rapport `rapport_2026-08-15_2030_evenements_xapi_progres.md` produit.
- [x] ADR-014 écrite ; ADR-012 condition 6 passée à « remplie » et condition 7
      complétée. **Plus aucune condition d'ADR-012 n'est entièrement à faire** ;
      restent l'antivirus et la vérification de licence, partielles.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #22 fusionnée le 15 août 2026, commit de
      fusion `d27f49f`, API CI et Secret Scan verts sur la Pull Request puis sur
      `main`.

Cette dernière ligne ne peut par construction être écrite qu'après la fusion : ce
qu'elle consigne n'existe pas encore quand la Pull Request de l'étape est
ouverte. Elle arrive donc dans un commit séparé, et c'est la seule raison pour
laquelle une étape en compte deux — l'audit du 15 août avait relevé qu'elle
manquait pour l'étape 10.

### Points ouverts de l'étape 11

- [x] **Refermé le 16 août 2026 par l'étape 13.** La route a désormais un
      appelant : le lecteur de contenu du web écoute le `postMessage` de
      `play.html` et relaie par `POST /api/xapi`. Éprouvé sur la pile vivante.
- **Ce n'est pas un LRS** : ni `GET` par requête xAPI, ni `voided`, ni version de
  spec négociée. C'est écrit dans la documentation pour ne pas laisser croire à
  une conformité que rien ne teste.
- **`SECRET_KEY` vide n'empêche pas le démarrage**, alors qu'elle dérive
  désormais le pseudonyme d'acteur xAPI. Le propriétaire a arbitré le 15 août
  2026 que ce durcissement appartient à l'étape 15 ; il est inscrit dans sa
  fiche 15.2 plutôt que traité par anticipation.
- Résorbé le 15 août 2026, Pull Request #24 : les contrôles ne se jouaient que
  dans le conteneur. `db.py` lisait `DATABASE_URL` dans `os.environ` quand tout
  le reste passe par les settings, PostgreSQL n'était publié nulle part, et les
  deux fichiers d'exemple décrivaient un état révolu. 499 tests verts des deux
  côtés.

## Résultats techniques de l'étape 11

```text
Ruff       : vert, format inclus, 119 fichiers
Mypy       : vert sur 66 fichiers
Alembic    : 0010_xapi_statements (head), check vert, downgrade base et retour au head
Pytest     : 499 tests réussis, dont 58 dédiés aux événements et aux progrès
Tests      : sans ticket, ticket inconnu ou ticket d'une autre famille, même refus
Tests      : le serveur déduit la tentative du ticket, le client ne la nomme pas
Tests      : cinq envois du même événement laissent une seule réponse
Tests      : l'acteur revendiqué n'est conservé nulle part
Tests      : l'URL de lecture ne porte ni enfant, ni pseudonyme, ni code famille
Tests      : les deux horloges d'un événement restent distinctes
Tests      : l'événement du runtime prime, qu'il parle avant ou après
Tests      : une tentative non terminée ne compte jamais dans les progrès
Tests      : aucun ratio ni score dans la charge utile des progrès
Tests      : deux lectures des progrès rendent exactement la même chose
```

## Étape 12, diagnostic et remédiation, clôturée

Travaux menés sur la branche `feat/etape-12-diagnostic`. Sous-étapes enchaînées
sans arrêt ; les décisions prises par l'agent sont consignées dans ADR-015.

### Ce que l'étape ajoute, et ce qu'elle refuse d'ajouter

La plateforme savait dire ce qu'un enfant avait fait et ce que chaque tentative
avait conclu. Elle ne disait nulle part qu'il y avait une difficulté. L'étape 12
le dit — et le dit de telle façon qu'aucune conclusion n'échappe à son
explication. **Aucune migration** : le diagnostic se calcule à chaque lecture.

### 12.1, règles de diagnostic, terminée

- [x] Cinq règles nommées, publiées par `GET /api/v1/diagnostic/rules`, toutes de
      l'arithmétique sur des comptes. Aucun modèle, opaque ou non.
- [x] **Une seule lecture intermédiaire n'est pas une difficulté** : c'est ce à
      quoi ressemble un apprentissage en chemin. Elle le devient si elle survit à
      une deuxième tentative terminée.
- [x] **Une compétence jamais travaillée n'est pas une lacune.** La ranger sous
      « difficulté » ferait d'une absence une accusation — la même règle qu'à
      l'étape 10, où l'absence de preuve n'écrit aucun résultat.
- [x] Le regroupement par domaine **ne supprime pas ce qu'il regroupe** : les
      compétences d'une lacune générale restent listées une par une, les deux
      listes côte à côte.
- [x] Une cause racine est une arête entre **deux** lacunes. Un prérequis acquis
      est une preuve contre l'hypothèse ; un prérequis jamais travaillé n'est
      aucune preuve. `confirmed` est un champ toujours faux, pas un sous-entendu.

### 12.2, moteur de remédiation, terminée

- [x] Une Quick Repair dure **de 3 à 7 minutes**. Hors bande, elle n'est pas
      proposée, si bien assortie soit-elle : proposer vingt minutes comme
      réparation rapide rendrait la promesse fausse.
- [x] Une seule activité par compétence, **causes racines d'abord**. Commencer
      par ce qui est dessous est tout l'intérêt d'avoir cherché.
- [x] Jamais proposée d'abord ; sinon déjà terminée, reproposée et **signalée**,
      parce que la refaire est une seconde passe ; jamais celle qui l'attend déjà.
- [x] Chaque recommandation **nomme sa preuve finale**, la lecture de la
      tentative. Rien n'y est marqué comme réparé.

### 12.3, API du diagnostic, terminée

- [x] Le diagnostic au Parent, les prochaines actions à l'Élève, par **deux
      routes distinctes** — une route unique à identifiant facultatif serait à un
      contrôle oublié près de montrer à une enfant ce qui n'est pas pour elle.
- [x] Une enfant voit une activité et sa durée ; ni le score, ni les lacunes, ni
      la règle qui a nommé une difficulté. Ce n'est pas du secret sur son propre
      travail : ses tentatives, ses résultats et ses progrès restent à sa
      disposition. C'est qu'une liste de réparations remise à une enfant *comme un
      diagnostic* est un jugement auquel elle n'a aucun moyen de répondre.

### Le score de santé, et la règle qu'il devait ne pas casser

- [x] Le produit demande un score ; une règle non négociable dit qu'une note ne
      remplace jamais une compétence. Les deux tiennent par trois propriétés et
      non par un compromis : le score apparaît **une fois pour un enfant**, à côté
      de la lecture par compétence qu'il résume et jamais à la place de l'une
      d'elles ; il est calculé sur ce que cette enfant a travaillé et **sur rien
      d'autre**, ni le programme ni d'autres enfants ; chacun de ses termes voyage
      avec lui, donc il se démonte.
- [x] **Rien d'observé ne rend aucun score.** Pas de zéro pour cela : zéro dirait
      que le travail s'est mal passé, alors qu'il n'a pas eu lieu.

### 12.4, clôture, terminée

- [x] Séquence complète de l'API CI rejouée, depuis la machine et dans le
      conteneur, tout vert, 544 tests dont 45 pour cette étape.
- [x] Rapport `rapport_2026-08-16_1030_diagnostic_remediation.md` produit.
- [x] ADR-015 écrite, registre des décisions mis à jour.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #26 fusionnée le 16 août 2026, commit de
      fusion `01a259a`, API CI et Secret Scan verts sur la Pull Request puis sur
      `main`.

### Corrections du propriétaire, 16 août 2026

Travaux menés après la clôture, en deux temps, sur les branches
`feat/remediation-reglable` puis `chore/retirer-mode-automatique`. Migrations
`0011` et `0012` réversibles. ADR-015 amendée.

- [x] **Une compétence dont le prérequis est en lacune n'est plus proposée du
      tout**, au lieu d'être proposée en second. Le propriétaire a rappelé
      l'intention : « ne pas lui demander d'assurer des opérations mathématiques
      alors que le vrai problème c'est le comptage, lui demander de conjuguer
      alors qu'il peine à reconnaître les groupes de verbes ». Sixième règle
      publiée, `defer-behind-prerequisite`. La lacune reportée **reste
      affichée**, avec ce qu'elle attend : reporter ce qu'on fait travailler
      n'est pas cacher ce qu'on a trouvé. Les chaînes se règlent seules.
- [x] **Le score est pondéré par le nombre de tentatives terminées.** Une
      compétence reprise dix fois pèse dix fois une compétence vue une seule. Le
      total des tentatives voyage avec le score : une moyenne pondérée dont le
      dénominateur est caché n'est pas vérifiable.
- [x] `POST /children/{id}/remediation` **donne les propositions sur la parole du
      parent**. Ce que la route retire est la ressaisie, pas la décision.

### Un aller-retour sur l'automatisation, et ce qu'il laisse

L'agent avait d'abord refusé toute assignation automatique. Le propriétaire a
infirmé — « le système doit pouvoir faciliter la tâche au parent […] mais tout ça
doit être réglable par le parent » — et un mode `automatic` par enfant a été
construit. Il a ensuite tranché : « on abandonne le mode automatique pour le
moment, on reste comme avant ».

- [x] Mode automatique retiré, migration `0012` : `auth_children.remediation_mode`
      et `assignments.origin` supprimées. Une colonne à valeur unique se lit comme
      une distinction que le code ferait ; la garder « pour plus tard » coûterait
      un malentendu à chaque rencontre.
- [x] **La plateforme n'assigne rien d'elle-même.** Ni à la lecture d'un
      diagnostic, ni à la clôture d'une tentative.
- [x] Arbitrage à retenir si l'automatisation revient : le réglage appartient au
      **parent**, avec une valeur par enfant — et non au profil de l'enfant, ce
      que l'agent avait choisi.
- [x] La leçon de conception : retirer une ressaisie est de l'ergonomie, choisir
      ce qu'un enfant fera est une décision. La plateforme fait la première et
      laisse la seconde.
- [x] 559 tests au total : neuf tests disparaissent avec la fonctionnalité qu’ils
      éprouvaient.

### Points ouverts de l'étape 12

- **Aucune notification**, et plus rien à notifier automatiquement : le « puis
  aviser le parent » demandé le 16 août attend l'étape 14, et n'a de sens que si
  une automatisation revient.
- Sans édition du référentiel en vigueur, les lacunes sont rendues mais ni
  regroupées ni expliquées par un prérequis ; `tree_available` le dit, pour
  qu'une réponse courte ne se lise pas « aucune difficulté ».

## Résultats techniques de l'étape 12

```text
Ruff       : vert, format inclus
Mypy       : vert sur 72 fichiers
Alembic    : 0012_drop_automatic_remediation (head), check vert, downgrade base et retour au head
Pytest     : 559 tests réussis, dont 60 dédiés au diagnostic
Tests      : une compétence jamais travaillée n'est jamais une lacune
Tests      : une lecture intermédiaire seule n'est pas une lacune, deux le sont
Tests      : les lacunes regroupées restent listées une par une
Tests      : un prérequis acquis n'explique rien
Tests      : une cause racine n'est jamais marquée comme établie
Tests      : une activité de vingt minutes n'est jamais une Quick Repair
Tests      : la cause racine est recommandée avant ce qu'elle explique
Tests      : une activité déjà en attente n'est pas reproposée
Tests      : rien d'observé ne rend aucun score
Tests      : le score porte chacun de ses termes et ne compare à personne
Tests      : l'Élève ne reçoit ni score, ni lacune, ni code de règle
Tests      : réparer le prérequis fait disparaître l'hypothèse, sans rafraîchir
Tests      : une compétence dont le prérequis est en lacune n'est pas proposée
Tests      : la lacune reportée reste affichée, avec ce qu'elle attend
Tests      : une compétence reprise dix fois pèse dix fois celle vue une seule
Tests      : lire le diagnostic n'affecte rien
Tests      : terminer une tentative n'affecte rien
Tests      : le parent donne les propositions en un appel
Tests      : appliquer deux fois n'ajoute rien et le dit
```

## Étape 13, tableaux de bord, clôturée

Travaux menés sur la branche `feat/etape-13-dashboards`. Sous-étapes enchaînées
sans arrêt ; les décisions sont consignées dans ADR-016.

### La première fois que le web appelle l'API

Le web était le prototype de l'étape 05 : des pages statiques, un bandeau
« données fictives » sur chacune, pas une requête. Côté API, tout existait depuis
six étapes et rien ne l'appelait. L'étape 13 les réunit — et c'est la première
fois qu'il faut dire **comment**.

### La décision qui gouverne l'étape, ADR-016

- [x] **Le navigateur ne connaît que l'origine du web.** Les composants serveur
      lisent le cookie de session et appellent l'API eux-mêmes. Un appel direct
      exigerait un cookie tiers `SameSite=None` — la forme que les navigateurs
      suppriment — et exposerait la session à tout ce que la page charge.
      Que `localhost:3000` et `localhost:8000` soient « même site » rend le
      problème invisible en développement et bien réel en production : une
      architecture qui ne marche qu'en local échoue au moment où c'est cher.
- [x] **Des actions serveur nommées une par une**, pas de proxy générique : un
      proxy ferait du web une seconde porte d'entrée de l'API, chaque route
      devenant joignable par un chemin que personne n'a écrit.
- [x] **Le garde d'accès est dans le layout, pas dans un middleware** : un
      middleware déciderait de la seule présence du cookie, et un cookie dont
      Redis ne détient plus la session ressemble exactement à un cookie valide.
      C'est l'API qui décide, toujours.
- [x] `GET /api/v1/auth/session` ajouté : sans lui un client devrait provoquer un
      `403` pour savoir qui il sert.

### 13.1, espace Élève, terminée

- [x] Cinq pages sur données réelles. **L'activité en cours passe avant tout** :
      c'est le seul élément réellement urgent, et l'enterrer sous la liste de ce
      qui reste serait le plus sûr moyen qu'elle ne soit jamais finie.
- [x] **Aucun diagnostic nulle part** : ni score, ni lacune, ni nom de règle. Ses
      résultats et sa progression restent à sa disposition et s'expliquent.
- [x] Rien n'est classé par gravité : une page qui s'ouvrirait sur les échecs
      serait une page sur l'échec.

### Le point ouvert de l'étape 11, refermé

- [x] `POST /api/xapi` est la **seule** route d'API du web, et elle relaie sans
      rien décider. `play.html` remontait ses événements depuis `PRE-01` sans
      destinataire ; il en a un.
- [x] **Le contrôle d'origine du `postMessage` est la mesure de sécurité de cette
      boucle.** `postMessage` livre à une fenêtre et non à un destinataire :
      sans vérifier `event.origin`, n'importe quelle frame ou extension pourrait
      déposer des réponses au nom d'un enfant. L'origine attendue vient de l'URL
      rendue par l'API, donc rien dans une requête ne la déplace.

### 13.2, espace Parent, terminée

- [x] Six pages. **Chaque conclusion porte la phrase qui l'a produite** : un
      parent qui ne peut pas discuter une conclusion se fait dire quoi penser.
- [x] Les **lacunes reportées sont montrées à part**, avec ce qu'elles attendent,
      et ne sont comptées ni dans les points d'attention ni dans les
      notifications : les signaler pousserait vers la compétence que la
      plateforme a décidé de ne pas travailler encore.
- [x] `/parent/parametres` publie les règles de lecture et de diagnostic — la
      page pour laquelle elles avaient été publiées — et dit pourquoi il n'y a
      rien à régler.

### 13.3, notifications, terminée

- [x] **Rien n'est envoyé nulle part.** Aucun e-mail, aucune alerte, rien de
      stocké, aucun état « lu » — donc **pas de pastille de non-lus**, parce
      qu'une pastille revendiquerait un état que personne ne tient. La page le
      dit en toutes lettres : c'est la lecture stricte du « sans automatisme
      trompeur » de la fiche.
- [x] Le calcul est côté web et non dans l'API : un modèle de notification avec
      sa remise et son état de lecture est le sujet de l'étape 14, et en inventer
      la moitié maintenant laisserait cette étape discuter avec une
      demi-implémentation.

### 13.4, clôture, terminée

- [x] **La boucle du MVP jouée de bout en bout sur la pile vivante** : activité
      donnée, commencée, contenu joué sur son origine isolée, événement xAPI
      relayé et dédupliqué, tentative lue, santé académique affichée au parent.
      Les preuves sont dans le rapport ; les données ont été supprimées ensuite.
- [x] Rapport `rapport_2026-08-16_2200_dashboards.md` produit.
- [x] Une seule Pull Request pour toute l'étape.
- [x] Clôture distante : Pull Request #30 fusionnée le 16 août 2026, commit de
      fusion `646b172`, API CI, Web CI et Secret Scan verts sur la Pull Request
      puis sur `main`. **Web CI passe pour la première fois sur du code qui
      appelle l'API.**
- [x] Un défaut trouvé par la CI et corrigé dans la même Pull Request : `lib/`,
      hérité de la section Python du `.gitignore`, avalait `apps/web/lib/`.
      Cinq fichiers de source n'étaient jamais arrivés dans le dépôt — le
      typage passait en local et ne pouvait pas passer en CI. C'est la
      cinquième fois sur ce projet qu'un contrôle dit une chose ici et une
      autre là ; celle-ci vient d'un motif d'exclusion non ancré.

### Points ouverts de l'étape 13

- **Aucun test automatisé du web.** La CI tient TypeScript, ESLint et le build ;
  les parcours ont été éprouvés à la main. C'est la dette principale de l'étape :
  un rendu qui régresse ne sera vu par personne. `vitest` est déclaré dans
  `package.json` sans être installé ni lancé, ce qui est le point de départ
  naturel pour la résorber.
- **Un appel d'API par enfant** sur le tableau de bord Parent. À la taille d'une
  famille cela ne se mesure pas ; à celle d'une classe, il faudra une lecture
  groupée.
- **Aucun écran d'administration des profils** : créer, activer et désactiver un
  enfant restent des appels d'API. C'est l'étape 15.

## Résultats techniques de l'étape 13

```text
Ruff        : vert, format inclus
Mypy        : vert sur 72 fichiers
Pytest      : 562 tests réussis, dont 3 pour GET /auth/session
TypeScript  : vert
ESLint      : vert
Build Next  : vert, 19 routes
Pile vivante : /eleve sans session redirige, avec session affiche l'activité
Pile vivante : la page de lecture rend l'iframe vers l'origine de contenu
Pile vivante : POST /api/xapi rend 202, le rejeu ne stocke rien de plus
Pile vivante : l'acteur revendiqué n'est pas conservé, un pseudonyme l'est
Pile vivante : la tentative terminée rend « 1 réponse évaluée, dont 1 juste »
Pile vivante : le parent voit la santé académique et sa phrase
```

## Travaux hors étape, 17 août 2026

Menés après la clôture de l'étape 13 et avant l'ouverture de l'étape 14, sur
autorisation permanente du propriétaire.

### Examen d'initiation et création de comptes

- [x] **La première marche du parcours, qui manquait.** La définition du MVP dit
      « parent crée un enfant → enfant réalise un diagnostic → … » ; la deuxième
      flèche n'existait pas. Un enfant inscrit n'avait aucune compétence
      observée, donc aucun diagnostic, donc aucune recommandation. Un examen de
      douze questions, une par compétence, est donné par la plateforme à
      l'activation — le seul endroit où elle assigne quoi que ce soit.
- [x] Défaut trouvé et corrigé : l'examen n'était donné qu'à l'*activation*, ce
      qui n'arrive jamais pour un profil qu'un parent crée lui-même, puisqu'il
      naît actif. Le chemin le plus probable était celui qui menait à un tableau
      de bord vide.
- [x] **Le balayage de tests supprimait des comptes qui n'étaient pas à lui.**
      Il effaçait tout compte en `example.com`, domaine réservé par la RFC 2606
      et donc exactement celui qu'une personne tape pour se créer un compte à la
      main. Il ne reconnaît plus qu'une **forme** générée — préfixe, tiret, les
      trente-deux caractères d'un `uuid4().hex` — et quinze tests nomment des
      adresses qu'un humain écrirait.
- [x] Quatre pages d'authentification distinctes (`/connexion`,
      `/connexion/eleve`, `/inscription`, `/inscription/eleve`). Les deux
      connexions partageaient une adresse derrière des onglets : un navigateur ne
      peut pas distinguer deux formulaires à une même adresse, et versait le mot
      de passe du parent dans « Code de la famille ». **Le remplissage
      automatique n'est pas désactivé** — c'est un service rendu, et la correction
      consiste à décrire les formulaires correctement, pas à les refuser.
- [x] La moitié des questions de français **contenaient leur réponse**. Réécrites,
      et quatorze propriétés les tiennent désormais.

### Identité visuelle, « le cahier »

- [x] Papeterie scolaire française — réglure Seyès, trait de marge, encre
      bleu-noir — et **une règle prise dans le produit : le rouge ne dit jamais
      qu'un enfant s'est trompé.** Ce qui demande du travail est ocre ; le rouge
      reste aux pannes techniques, derrière un jeton distinct.
- [x] Signature : le **fil de prérequis**, une chaîne rendue où une compétence
      reportée se lit derrière celle qui la bloque. Il n'existe que là où une
      relation de prérequis existe.
- [x] Atkinson Hyperlegible pour le texte courant, choisie parce qu'elle a été
      dessinée pour que le b et le d cessent de se ressembler — ce que l'examen
      mesure justement.
- [x] L'indicateur de santé n'est plus un chiffre géant : son explication passe
      devant. Un grand nombre isolé se lit comme une note.
- [x] Trois jetons de couleur échouaient au contraste AA et ont été assombris.
- [x] Pull Request #41 fusionnée, commit `0866010`.

### Fiches de remédiation, ADR-017

- [x] **Les douze remédiations étaient des lignes de catalogue sans rien
      derrière.** Le diagnostic proposait des réparations qui s'ouvraient sur une
      page vide. Douze fiches écrites ici : trois à sept minutes, une leçon, quatre
      questions, une explication après chacune.
- [x] Décision consignée en ADR-017 : écrire plutôt qu'importer. Le rattachement
      question-compétence n'existe nulle part ailleurs, ADR-012 n'autorise qu'une
      bibliothèque, l'origine de contenu n'est pas déployable sur Render, et une
      réparation doit enseigner avant d'interroger.
- [x] `assessment_questions` devient `authored_questions` : la table sert les deux
      natures écrites ici. La correction est mutualisée, **ce que chacune répond
      ne l'est pas** — une fiche explique, l'examen se tait, sans quoi il
      cesserait de mesurer.
- [x] **Une faille ouverte par cette asymétrie, et fermée.** Sans contrôle de la
      nature de l'activité, une enfant pouvait poster ses réponses d'examen à la
      route des fiches et se faire dire, une par une, si elles étaient justes.
      L'examen serait devenu franchissable par la porte ouverte pour l'aider.
- [x] Quatre questions ont été prises en défaut par les propriétés et réécrites :
      trois dont la réponse était recopiable dans l'énoncé, une sans point
      d'interrogation.
- [x] Le paquet H5P vérifié garde une activité à lui, en dehors des douze
      réparations : le runtime de contenu reste démontrable, et plus rien du
      parcours ne dépend de son déploiement.
- [x] Migration `0014_remediation_sheets`, réversible, vérifiée par
      `downgrade base` puis `upgrade head`.

### Contenus H5P et PhET, ADR-012 amendée

- [x] **ADR-012 amendée sur validation du propriétaire : huit types au lieu
      d'un.** Un seul type ne peut pas porter une matière — une dictée doit
      s'entendre, un rangement doit se manipuler. `H5P.Dictation` est le seul qui
      paie une dette réelle : tout le reste, la plateforme sait déjà le demander
      dans une fiche qu'elle a écrite.
- [x] `QuestionSet` reste refusé faute d'attribution par sous-contenu,
      `ArithmeticQuiz` parce qu'il chronomètre un enfant.
- [x] **La version cesse d'être épinglée.** Le gel est assuré par l'empreinte,
      qui distingue deux compilations d'une même version là où une chaîne de
      version ne le peut pas. Migration `0015_h5p_allowed_libraries`, réversible.
- [x] `python -m app.catalog libraries` extrait les bibliothèques d'un `.h5p`
      téléchargé et les fusionne dans l'arbre partagé, **sans jamais écraser**
      une bibliothèque déjà vérifiée.
- [x] **Piège consigné et signalé par la commande** : un `.h5p` peut ne contenir
      aucune bibliothèque. Le paquet du pilote lui-même est de cette forme —
      c'est pourquoi ses bibliothèques avaient dû être préparées à la main.
      Répondre « rien à ajouter » aurait été indiscernable du cas anodin.
- [x] Liste de courses écrite : `docs/contenus/a-telecharger.md`.

### Démonstration par tunnel

- [x] **Ce qui bloque Render, en une phrase** : l'API écrit les contenus dans un
      dossier, nginx les lit dans ce même dossier, et sur Render un disque
      n'appartient qu'à un seul service. Ce n'est pas un défaut, c'est une limite
      d'hébergeur qui rencontre l'exigence d'origine séparée d'ADR-012.
- [x] **Un tunnel n'est pas un contournement** : la pile locale est la pile
      complète, origine isolée et tickets compris. Elle montre plus que Render ne
      pourrait, H5P compris.
- [x] **Défaut trouvé avant la démonstration** : Next vérifie l'origine de chaque
      action serveur, et derrière un tunnel l'hôte public ne correspond pas —
      *toute connexion aurait échoué*, puisque se connecter est une action
      serveur. `PUBLIC_HOST` déclare l'hôte du tunnel ; sans la variable, rien
      n'est ouvert.
- [x] Recette écrite : `docs/deploiement/demonstration-par-tunnel.md`.

### Six classes cumulatives, ADR-018

- [x] **L'élémentaire compte six classes**, du CI au CM2, et non deux. Trente-six
      compétences, six par classe, trois par matière. Les niveaux ne sont pas
      écrits en dur : ils appartiennent à l'édition du référentiel, seule
      autorisée à dire de quoi l'élémentaire est fait.
- [x] **Les compétences sont cumulatives** : un CE2 doit celles du CI, du CP, du
      CE1 et du CE2. Ce n'est pas une convention d'affichage — c'est ce qui rend
      le diagnostic capable de descendre.
- [x] **Un examen d'entrée par classe**, six questions, une par compétence du
      niveau. Il ne porte que sur la classe déclarée : un examen qui balaierait
      les six ferait trente-six questions à un CM2, et aucun enfant ne le
      finirait.
- [x] **La classe est demandée à l'inscription**, sur les deux chemins, et jamais
      devinée. Colonne nullable : un profil ouvert avant que la plateforme ne la
      demande existe, et lui en attribuer une d'office affirmerait sur un enfant
      réel ce que personne n'a dit. Une route la déclare ou la corrige après coup.
- [x] **Le passage en classe supérieure est décidé par le parent.** La plateforme
      ne connaît ni l'école, ni l'année scolaire, ni ce qu'un conseil de maîtres a
      tranché. Chaque passage est une ligne datée dans `auth_child_promotions` ;
      rien ne s'y met à jour.
- [x] **Le palier monte, rien n'est effacé.** Toutes les lectures des classes
      antérieures restent, et c'est ce qui permet de remonter une lacune ancienne.
- [x] **Règle nouvelle, `unobserved-prerequisite`.** Un examen ne portant que sur
      la classe déclarée, les compétences antérieures n'ont aucune lecture ; sans
      cette règle la plateforme constaterait l'échec sans rien pouvoir remonter,
      et proposerait de refaire ce qui vient d'échouer. Vérifié sur la pile
      vivante : Léa, en CE1, voit ses quatre lacunes reportées et la plateforme
      propose deux fiches de **CP**.
- [x] Migration `0016_classe_et_passage`, réversible.
- [x] Dix-huit tests pour les classes et le passage, dans un module qui **publie
      sa propre édition** : une première version lisait celle en vigueur et se
      sautait quand elle n'en trouvait pas assez, ce qui n'aurait jamais rien
      éprouvé sur une base neuve.

### Dette assumée et mesurée

- **Vingt-quatre compétences sur trente-six n'ont pas de fiche de remédiation.**
  Les douze existantes couvrent du CI au CE1. Un test épingle la couverture dans
  les deux sens : il échoue si une fiche disparaît, et il échoue quand de
  nouvelles arrivent, pour que la dette ne baisse pas sans qu'on la voie baisser.
- **Les examens du CI sont les plus fragiles du référentiel** : un enfant de cours
  d'initiation ne lit pas encore, et un examen écrit lui demande de déchiffrer la
  question.

## Résultats techniques du 17 août 2026

```text
Ruff        : vert, format inclus
Mypy        : vert sur 84 fichiers
Pytest      : 1135 tests réussis
TypeScript  : vert
ESLint      : vert
Build Next  : vert, 20 routes
Migrations  : 0014 et 0015 réversibles, aller-retour complet vérifié
Base        : 12 compétences, examen à 12 questions, 12 fiches à 4 questions
              expliquées chacune ; l'examen n'a aucune explication, par décision
```

## Dettes connues

- **Aucun test automatisé du web.** `vitest` est déclaré sans être installé.
  C'est la dette principale, inchangée depuis l'étape 13.
- **Aucun son.** Les questions de phonologie, dans l'examen comme dans les
  fiches, parlent de mots écrits. C'est la première chose à ajouter si la
  plateforme sert en vrai.
- **Aucune image.** Le dénombrement se fait sur des rangées de symboles
  typographiques : cela tient jusqu'à une dizaine.
- **Un appel d'API par enfant** sur le tableau de bord Parent.
- **Aucun écran d'administration des profils** : étape 15.
- **ADR-012** : antivirus et vérification de licence encore partiels.

## Contenus H5P, la liste par compétence

- [x] `docs/contenus/exercices-par-competence.md` : un exercice concret par
      compétence sur les trente-six, avec le type H5P recommandé et ce qu'il
      faut construire. Les douze déjà couvertes par une fiche native ne
      reçoivent qu'un seul exercice, réservé à ce qu'une fiche ne sait pas
      faire — le son, le geste. Les vingt-quatre sans rien reçoivent un jeu
      complet.
- [x] `docs/contenus/a-telecharger.md` corrigé : il citait des codes de
      compétence disparus depuis la restructuration à six classes
      (`cp-ma-denombrer`, `ce1-fr-comprehension`).
- [x] Quatre simulations PhET retenues, chacune adossée aux compétences
      qu'elle sert réellement plutôt qu'à la matière en général.

## Prochaine action

Le propriétaire fabrique et télécharge les fichiers H5P selon cette liste.
Ensuite : ouvrir l'étape 14, notifications.
