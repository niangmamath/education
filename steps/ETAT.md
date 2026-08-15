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

Les dossiers détaillés des étapes 09 à 16 sont temporairement retirés du dépôt. Chaque dossier rejoint le dépôt au démarrage de l’étape correspondante ; celui de l’étape 07 y est entré le 14 août 2026, celui de l’étape 08 le 15 août 2026.

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

### 07.3, API du référentiel, en revue

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

`steps/07_referentiel_competences/rapport_2026-08-15_1440_cloture_etape_07.md`.

## Historique de clôture de l’étape 06

- Pull Request #3 du 13 août : première coupe des modèles d’identité, fusionnée
  alors que la branche continuait d’évoluer.
- Pull Request #4 du 14 août : reste de l’étape 06. Elle est d’abord ressortie en
  conflit et sans aucun contrôle, GitHub ne lançant rien tant qu’il ne peut pas
  construire la fusion d’essai. `main` fusionnée dans la branche, conflits résolus
  du côté de la branche, qui portait déjà ce contenu et sa suite.
- Commit de fusion `a49ec43`, API CI et Secret Scan verts sur `main`.

## Étape 08, catalogue de contenus et activités, en cours

Travaux menés sur la branche `feat/etape-08-catalogue`.

## Prochaine action

Mener les sous-étapes 08.1 à 08.4.
