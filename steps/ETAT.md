# État du projet

## Référence

- Projet : StudentConnect
- Date : 13 août 2026
- Dépôt : `Tidianesarrndiaye-org/StudentConnect`
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

Les dossiers détaillés des étapes 04 à 16 sont temporairement retirés du dépôt. Chaque dossier sera régénéré proprement au démarrage de l’étape correspondante.

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

## Étape 06, backend identité et famille, en cours

Travaux menés sur la branche `feat/backend-identity-family`, non fusionnée.

### 06.1, modèles Parent et Enfant, en revue

- [x] Modèles SQLAlchemy `Parent` et `Child`, relation familiale en cascade.
- [x] Migration `0002_identity_family_models`, réversible jusqu’à `base`.
- [x] Dérive entre modèles et migration corrigée sur `auth_parents.email` :
      l’unicité vient d’une `UniqueConstraint` nommée, l’index redondant a été
      retiré et `alembic check` est vert.
- [x] `alembic check` et le cycle downgrade puis upgrade ajoutés à l’API CI.
- [ ] Validation indépendante et clôture distante.

### 06.2, authentification Parent et sessions, en revue

- [x] Routes `POST /api/v1/auth/parent/register`, `POST /api/v1/auth/parent/login`,
      `DELETE /api/v1/auth/logout` et `GET /api/v1/auth/me`.
- [x] Mots de passe hachés en Argon2id, réponses identiques pour un mot de passe
      erroné et une adresse inconnue.
- [x] Sessions opaques en Redis, indexées par l’empreinte du jeton, cookie
      `HttpOnly` et `SameSite=lax`, révocation immédiate à la déconnexion.
- [x] Aucune table SQL de session, conformément à ADR-005.
- [ ] Validation indépendante et clôture distante.

### Points ouverts

Les stratégies de résolution des trois premiers points sont décrites dans
`docs/backend/points-ouverts-authentification.md`.

- ADR-005 cite bcrypt dans un extrait illustratif alors que l’implémentation
  retient Argon2id ; l’ADR reste à amender. À trancher avant que de vrais comptes
  n’existent, car aucune migration automatique ne franchit un changement
  d’algorithme.
- La vérification d’adresse email prévue par ADR-005 n’est pas implémentée faute
  de service d’envoi ; `is_verified` reste à `false` et la connexion ne l’exige pas.
- Aucune limitation de débit sur la connexion, alors que `RATE_LIMIT` et
  `RateLimitException` existent déjà sans être branchés.
- [x] `argon2-cffi` intégré aux images `api` et `worker` reconstruites.
- [x] `steps/MANIFESTE.md` régénéré depuis l’arborescence réelle, avec la règle
      d’inventaire et la commande de régénération.

## Résultats techniques de l’étape 06

```text
Alembic    : 0002_identity_family_models (head), downgrade base puis upgrade head validés
Alembic    : check vert, aucune dérive entre modèles et base
Ruff       : vert, format inclus, 45 fichiers
Mypy       : vert sur 20 fichiers
Pytest     : 51 tests réussis
API vivante: register 201, login 200 avec cookie durci, me 200, logout 204, me 401
```

## Prochaine action

Valider 06.1 et 06.2 de manière indépendante, puis engager `03_acces_enfant.md`.
