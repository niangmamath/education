# Rapport de réalisation

## Métadonnées

- Étape : 06, backend identité et famille
- Sous-étape : 06.4, clôture, couvrant la validation de 06.1, 06.2 et 06.3
- Date et heure : 14 août 2026
- Agent : Claude Code
- ID du planning : BE-01 à BE-04
- Branche : `feat/backend-identity-family`
- Commit ou pull request : `254f9a1`, `983ed51`, `62f40af`, `ae97bd9`, `ff58ed0`,
  `da601ca`, fusion `81da709`, `59d2ee4` ; Pull Request #4 fusionnée dans `main`
  par le commit `a49ec43`
- Statut : Terminé

## Objectif

Implémenter l'identité Parent et Enfant, les relations familiales et les sessions
serveur conformément à ADR-005, puis valider migrations, sécurité, tests et
documentation avant fusion.

## Prérequis vérifiés

- Branche dédiée `feat/backend-identity-family` issue de `main`.
- Services Docker `postgres`, `redis`, `storage`, `api` et `worker` sains.
- ADR-005, `DECISIONS_FINALES.md` et les fiches 06.1 à 06.4 relus.
- Aucune donnée réelle : toutes les adresses de test appartiennent à
  `example.com`, réservé par la RFC 2606, et tous les enfants sont fictifs.

## État initial observé

06.1 et 06.2 étaient livrées et en revue, sans validation indépendante. 06.3 était
à faire. Le dépôt portait onze dossiers d'étape non suivis, situation antérieure à
cette étape et laissée telle quelle.

## Travaux réalisés

### Validation indépendante de 06.1 et 06.2

Séquence de l'API CI rejouée localement, puis parcours complet sur l'API vivante :
inscription, connexion, lecture du profil, déconnexion. Un mot de passe erroné et
une adresse inconnue rendent une réponse identique au corps près. La session
apparaît dans Redis sous l'empreinte du jeton, jamais sous le jeton, et disparaît
à la déconnexion.

### 06.3, création et accès Enfant

- Unicité du pseudonyme rendue **familiale** sur décision du propriétaire, à la
  place de l'unicité globale dérivée d'un extrait d'ADR-005.
- Code famille de six caractères frappé à l'inscription du Parent, alphabet sans
  caractères confondables à la lecture manuscrite, régénérable en cas de fuite.
- Création d'un profil par le Parent, auto-inscription par l'Enfant avec le code
  famille, activation et retrait d'une demande par le Parent, connexion Enfant,
  lecture du profil, déconnexion partagée avec le Parent.
- Trois états de profil, `pending`, `active` et `disabled`, à la place du booléen
  `is_active`.
- PIN de six chiffres haché en Argon2id, chiffre répété et suite continue refusés.
- Verrou sur les tentatives de PIN, compteur d'échecs par enfant en Redis.
- Session Enfant d'une journée contre sept pour le Parent.

### Clôture

Pull Request #4 ouverte vers `main`. Elle est d'abord ressortie en conflit, sans
aucun contrôle déclenché : la Pull Request #3 du 13 août avait fusionné une version
antérieure des mêmes fichiers, et GitHub ne lance rien tant qu'il ne peut pas
construire la fusion d'essai. `main` a été fusionnée dans la branche et les cinq
conflits résolus du côté de la branche, qui portait déjà ce contenu et sa suite,
dont le correctif de dérive retirant l'index redondant sur `auth_parents.email`.
L'arbre obtenu est identique à celui de la branche avant fusion. Les contrôles
distants se sont alors déclenchés et sont verts.

## Fichiers créés

- `apps/api/alembic/versions/0003_family_code_child_status.py`
- `apps/api/app/api/cookies.py`
- `apps/api/app/api/v1/children.py`
- `apps/api/app/core/lockout.py`
- `apps/api/tests/test_auth_child.py`
- `docs/backend/acces-enfant.md`
- `steps/06_backend_identite_famille/rapport_2026-08-14_cloture_etape_06.md`

## Fichiers modifiés

- `apps/api/app/api/deps.py`, `apps/api/app/api/v1/auth.py`
- `apps/api/app/core/config.py`, `apps/api/app/core/routing.py`,
  `apps/api/app/core/security.py`
- `apps/api/app/models/identity.py`, `apps/api/app/schemas/auth.py`
- `apps/api/tests/test_auth_parent.py`, `apps/api/tests/test_identity_models.py`,
  `apps/api/tests/test_security.py`
- `docs/backend/authentification-parent-sessions.md`,
  `docs/backend/modele-identite-famille.md`,
  `docs/backend/points-ouverts-authentification.md`
- `steps/DECISIONS_FINALES.md`, `steps/ETAT.md`, `steps/MANIFESTE.md`,
  `steps/PLANNING.md`, `steps/06_backend_identite_famille/README.md`,
  `steps/06_backend_identite_famille/03_acces_enfant.md`,
  `steps/06_backend_identite_famille/04_cloturer_etape.md`

## Commandes exécutées

```
docker compose exec -T api ruff format --check .
docker compose exec -T api ruff check .
docker compose exec -T api mypy app --ignore-missing-imports
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic check
docker compose exec -T api alembic downgrade -1
docker compose exec -T api alembic upgrade head
docker compose exec -T api alembic downgrade base
docker compose exec -T api alembic upgrade head
docker compose exec -T api pytest -q
```

## Tests exécutés

- 123 tests Pytest, dont 60 d'intégration contre PostgreSQL et Redis réels.
- Parcours manuels sur l'API vivante pour chaque route, à deux familles.

## Résultats des tests

```text
Alembic    : 0003_family_code_child_status (head)
Alembic    : check vert, aucune dérive entre modèles et base
Alembic    : downgrade -1, downgrade base et retour au head validés
Ruff       : vert, format inclus, 50 fichiers
Mypy       : vert sur 23 fichiers
Pytest     : 123 tests réussis
API vivante: deux familles créent chacune une « lea » en 201, doublon interne 409
API vivante: child login 200 par code famille, autre famille et code inconnu 401
API vivante: auto-inscription 201 en attente, connexion 403, activation 200
API vivante: régénération 200, ancien code 401 et 404, session ouverte intacte
API vivante: demande écartée 204, profil actif 409, autre famille 404
API vivante: cinq PIN erronés puis verrou 429, y compris avec le bon PIN
```

## Critères d'acceptation

- [x] Le Parent s'inscrit, se connecte et se déconnecte, sessions en Redis.
- [x] L'Enfant n'a ni email ni téléphone, seulement pseudonyme et PIN haché.
- [x] Le pseudonyme est unique dans la famille et jamais sur la plateforme.
- [x] Un Parent n'accède qu'aux enfants qui lui sont associés.
- [x] Aucune table SQL de session, conformément à ADR-005.
- [x] Migrations réversibles, `alembic check` sans dérive.
- [x] Formatage, lint, typage et tests verts.
- [x] Aucun secret ni donnée réelle dans le dépôt ou les journaux.
- [x] API CI et Secret Scan distants verts sur la Pull Request #4.
- [x] Fusion vers `main`, commit `a49ec43`, puis API CI et Secret Scan verts sur
      `main`.

## Décisions ou ADR

- L'unicité du pseudonyme est familiale ; le code famille du Parent est
  l'identifiant par lequel un Enfant atteint sa famille. Décision du propriétaire,
  inscrite dans `DECISIONS_FINALES.md`.
- Un Enfant peut créer son profil avec le code famille ; ce profil reste en attente
  jusqu'à activation par le Parent.
- Le verrou sur les tentatives de PIN est traité dans 06.3 plutôt que reporté à
  l'étape 15, le risque étant immédiat et le coût faible.
- Argon2id est retenu pour les mots de passe et les PIN. ADR-005 reste à amender,
  sur ce point comme sur celui de la connexion Enfant.

## Écarts par rapport au prompt

- ADR-005 décrit une connexion Enfant par pseudonyme et PIN seuls. La règle
  d'unicité familiale la rend impossible : la connexion exige désormais le code
  famille. L'écart est assumé et l'ADR reste à amender.
- Les commits et le push ont été réalisés par l'agent sur autorisation explicite du
  propriétaire, alors que le prompt d'exécution demande de s'arrêter avant `git add`.

## Risques ou dette technique

- Aucune limitation de débit sur la connexion Parent ; seule la connexion Enfant
  est protégée, et par profil et non par origine.
- La vérification d'adresse email d'ADR-005 n'est pas implémentée, faute de service
  d'envoi ; `is_verified` reste à `false`.
- Rien ne plafonne le nombre de profils en attente qu'un tiers connaissant un code
  famille peut créer, ni ne notifie le Parent.
- Le cycle de vie d'un profil actif n'est pas couvert : ni désactivation, ni
  suppression, ni changement de PIN.
- Le retour arrière de la migration `0003` est impossible tant que deux familles
  partagent un pseudonyme ; la migration s'arrête alors avec un message explicite.

## Blocages

Aucun.

## Prochaines actions

1. Amendement d'ADR-005 sur l'algorithme de hachage et sur la connexion Enfant.
2. Ouverture de l'étape 07, référentiel de compétences.

## Mise à jour appliquée à ETAT.md

Sections 06.1, 06.2 et 06.3 marquées validées localement avec leurs preuves, ajout
de la section 06.4, mise à jour des points ouverts et des résultats techniques.

## Mise à jour appliquée à PLANNING.md

Ajout de la phase 2 et des tâches BE-01 à BE-04 avec leurs preuves, et mise à jour
de la prochaine tâche.
