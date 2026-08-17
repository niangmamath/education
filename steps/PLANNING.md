# Planning simple de développement

## Principes

- Statuts : À faire, En cours, Bloqué, En revue, Terminé.
- Une tâche terminée doit disposer d’une preuve reproductible.
- Une tâche bloquée doit référencer un rapport.
- Le commit, le push et la CI distante font partie de la clôture d’une étape d’infrastructure.

## Phase 0, préparation et infrastructure

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| P0-01 | Vérifier le dépôt vidé | Aucune | Terminé | Rapport étape 01 |
| P0-02 | Recréer les fichiers racine | P0-01 | Terminé | README, gitignore, env example |
| P0-03 | Créer les ADR initiaux | P0-02 | Terminé | ADR et registre |
| P0-04 | Initialiser le monorepo | P0-03 | Terminé | Rapports étape 02 |
| S1-01 | Initialiser Next.js et Tailwind | P0-03 | Terminé | TypeScript, ESLint et build verts |
| S1-02 | Initialiser FastAPI | P0-03 | Terminé | API, CORS et tests verts |
| P0-05A | Configurer Docker Compose | P0-04, S1-02 | Terminé | Services healthy, Celery et buckets |
| S1-03 | Configurer SQLAlchemy et Alembic | S1-02, P0-05A | Terminé | Upgrade, downgrade et head |
| S1-07 | Configurer la CI | S1-01, S1-02, S1-03 | Terminé | API CI, Web CI et Secret Scan réussis |
| P0-05 | Clôturer l’infrastructure locale | P0-05A, S1-03, S1-07 | Terminé | Rapports, commits, push et CI distante |
| P0-06 | Réaliser le spike H5P | P0-05 | Terminé | Rendu True/False et événement xAPI validés |
| P0-07 | Geler les types H5P autorisés | P0-06 | Terminé | ADR-012, True/False pilote uniquement |

## Preuves de clôture de P0-05

- [x] Script global local terminé avec code `0`.
- [x] Rapports de l’étape 03 produits.
- [x] Commit principal `d7a7262` poussé sur `main`.
- [x] Correctif Secret Scan `6bcf765` poussé sur `main`.
- [x] API CI distante réussie.
- [x] Web CI distante réussie.
- [x] Secret Scan distant réussi.

### Phase 1, UX design et navigation

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| UX-01 | Définir les parcours utilisateurs | P0-07 | Terminé | Personas, parcours et matrice besoins-écrans |
| UX-02 | Définir les routes et la navigation | UX-01 | Terminé | Routes MVP et règles d’accès |
| UX-03 | Migrer le design system vers Bootstrap | UX-02 | Terminé | Bootstrap 5.3.8, Tailwind retiré, build vert |
| UX-04 | Concevoir l’espace Parent | UX-03 | Terminé | Layout et routes Parent validés |
| UX-05 | Concevoir l’espace Élève | UX-03 | Terminé | Layout et routes Élève validés |
| UX-06 | Valider les états et l’accessibilité | UX-04, UX-05 | Terminé | Validation manuelle et page accessibilité |
| UX-07 | Clôturer l’étape 05 | UX-06 | Terminé | Rapport, fusion et contrôles distants verts |

### Phase 2, backend identité et famille

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| BE-01 | Modéliser Parent et Enfant | UX-07 | Terminé | Migration `0002`, `alembic check` vert |
| BE-02 | Authentifier le Parent et ouvrir des sessions | BE-01 | Terminé | Sessions Redis, cookie durci, réponses indistinctes |
| BE-03 | Créer et connecter l’Enfant | BE-02 | Terminé | Code famille, unicité familiale, verrou PIN, 123 tests |
| BE-04 | Clôturer l’étape 06 | BE-03 | Terminé | Rapport du 14 août 2026, PR #4 fusionnée, CI verte sur `main` |
| BE-05 | Résorber la dette de l’étape 06 | BE-04 | Terminé | Cycle de vie du profil, retour arrière de `0003`, ADR-005 amendée |

### Preuves de clôture de BE-04

- [x] Rapport de validation produit et appliqué à `ETAT.md`.
- [x] Pull Request #4 fusionnée dans `main`, commit `a49ec43`.
- [x] API CI distante réussie sur la Pull Request puis sur `main`.
- [x] Secret Scan distant réussi sur la Pull Request puis sur `main`.

### Phase 3, référentiel de compétences

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| REF-01 | Modéliser le référentiel scolaire | BE-05 | Terminé | Migration `0004`, 23 tests de contraintes, rapport du 14 août 2026 |
| REF-02 | Importer un référentiel fictif de façon idempotente | REF-01 | Terminé | PR #11 fusionnée, CI verte sur `main`, rapport du 14 août 2026 |
| REF-03 | Exposer les lectures filtrées et paginées | REF-02 | Terminé | Commande `publish`, quatre routes, 37 tests, rapport du 15 août 2026 |
| REF-04 | Clôturer l’étape 07 | REF-03 | Terminé | Séquence de l’API CI rejouée, 255 tests, Pull Request unique |

### Phase 4, catalogue de contenus et activités

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| CAT-01 | Modéliser le catalogue et ses liens | REF-04 | Terminé | Migration `0005`, ADR-013, 27 tests de contraintes |
| CAT-02 | N’admettre que les types H5P d’ADR-012 | CAT-01 | Terminé | Vérification sans extraction, paquet pilote enregistré, 31 tests |
| CAT-03 | Exposer les lectures du catalogue | CAT-02 | Terminé | Trois routes, filtres, 23 tests |
| CAT-04 | Clôturer l’étape 08 | CAT-03 | Terminé | Séquence de l’API CI rejouée, 336 tests, Pull Request unique |

### Phase 5, affectations et parcours

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| AFF-01 | Modéliser l’affectation | CAT-04 | Terminé | Migration `0006`, index partiel, clé restrictive |
| AFF-02 | Exposer l’API Parent | AFF-01 | Terminé | Création, liste, annulation, isolation éprouvée |
| AFF-03 | Exposer l’API Élève | AFF-02 | Terminé | Liste, démarrage, achèvement, aucun retour arrière |
| AFF-04 | Clôturer l’étape 09 | AFF-03 | Terminé | Séquence de l’API CI rejouée, 361 tests, PR unique |

### Prérequis transverse

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| PRE-01 | Construire le runtime de contenu isolé | AFF-04 | Terminé | Origine isolée, tickets, déploiement, 23 tests |

`PRE-01` comble un trou du découpage initial : trois étapes présupposent un
runtime de contenu sans qu’aucune ne le construise. Il n’est le contenu d’aucune
étape, c’est le prérequis commun des étapes 10 et 11, fusionné avant elles.

### Phase 6, tentatives et résultats

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| TEN-01 | Modéliser tentatives et réponses | PRE-01 | Terminé | Migration `0008`, trois tables, aucune colonne de score |
| TEN-02 | Exposer l’API des tentatives | TEN-01 | Terminé | Démarrage idempotent garanti par un index partiel |
| TEN-03 | Calculer les résultats par règles explicites | TEN-02 | Terminé | Trois règles nommées, 15 tests isolés |
| TEN-04 | Clôturer l’étape 10 | TEN-03 | Terminé | Séquence de l’API CI rejouée, 434 tests, PR unique |
| TEN-05 | Résorber la dette de l’étape 10 | TEN-04 | Terminé | Attribution par question, provenance, règles publiées, 440 tests |

### Audit transversal

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| AUD-01 | Auditer la cohérence avant l’étape 11 | TEN-05 | Terminé | Huit incohérences corrigées, détaillées dans `ETAT.md` ; 441 tests |

`AUD-01` a relu le code, la documentation, les ADR, le registre, les fiches et
l’état du dépôt les uns contre les autres. Une seule des huit trouvailles était
un défaut de conception — les règles de lecture publiées n’étaient lisibles que
par l’Élève, alors qu’elles sont publiées pour le Parent. Une autre était un
contrôle qui ne disait pas la même chose en local et en CI. Les six dernières
étaient des documents décrivant un état révolu, ce qui est le mode de
vieillissement normal d’un projet mené par étapes et la raison d’être de cet
audit.

### Phase 7, événements xAPI et progrès

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| XAP-01 | Ingérer et valider les événements xAPI | AUD-01 | Terminé | Migration `0010`, endpoint autorisé par le ticket, rejeux dédupliqués |
| XAP-02 | Relier l’acteur pseudonyme à l’Élève | XAP-01 | Terminé | Acteur revendiqué remplacé par un pseudonyme HMAC ; URL de lecture sans identité, éprouvée |
| XAP-03 | Agréger les progrès | XAP-02, TEN-03 | Terminé | Progrès calculés à la lecture, sans table d’agrégats, sans ratio |
| XAP-04 | Clôturer l’étape 11 | XAP-03 | Terminé | 499 tests, rapport du 15 août 2026, ADR-014, ADR-012 condition 6 remplie |

L’étape 11 **dépend de l’étape 10** : `XAP-03` produit des agrégats « à partir
des événements et résultats », et ces résultats sont ceux de `TEN-03`. Un
décalage inverse avait été inscrit par erreur le 15 août 2026 ; il est corrigé.

### Phase 8, diagnostic et remédiation

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| DIA-01 | Définir les règles de diagnostic | XAP-04 | Terminé | Cinq règles nommées et publiées, `GET /api/v1/diagnostic/rules` |
| DIA-02 | Recommander une remédiation | DIA-01, CAT-03 | Terminé | Quick Repairs de 3 à 7 minutes, causes racines d’abord, preuve finale nommée |
| DIA-03 | Exposer le diagnostic et les prochaines actions | DIA-02 | Terminé | Diagnostic au Parent, actions à l’Élève, deux routes distinctes |
| DIA-04 | Clôturer l’étape 12 | DIA-03 | Terminé | 544 tests, rapport du 16 août 2026, ADR-015 |

| DIA-05 | Reporter derrière le prérequis, pondérer le score, éviter la ressaisie | DIA-04 | Terminé | Migrations `0011` et `0012`, sixième règle publiée, 559 tests |

Le diagnostic lui-même se calcule à chaque lecture et ne se stocke pas, ce qui
rend vraie par construction la règle « une cause racine reste une hypothèse
jusqu’à la réévaluation ». `DIA-05` applique les corrections du propriétaire : une compétence dont le
prérequis est en lacune n’est plus proposée du tout, le score est pondéré par le
nombre de tentatives, et une route évite au parent de ressaisir les propositions.
Un mode automatique a été construit puis **retiré à sa demande** ; la plateforme
n’assigne rien d’elle-même. ADR-015 amendée en conséquence.

### Phase 9, tableaux de bord

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| DASH-01 | Alimenter l’espace Élève | DIA-05 | Terminé | Cinq pages sur données réelles, activité en cours d’abord, aucun diagnostic |
| DASH-02 | Alimenter l’espace Parent | DASH-01 | Terminé | Six pages, chaque conclusion avec sa phrase, lacunes reportées montrées à part |
| DASH-03 | Présenter les notifications | DASH-02 | Terminé | Relecture des faits, aucune remise, aucun état de lecture, dit en toutes lettres |
| DASH-04 | Clôturer l’étape 13 | DASH-03 | Terminé | 562 tests, web vert, boucle du MVP jouée sur la pile vivante, ADR-016 |

`DASH-01` referme le point ouvert de l’étape 11 : l’endpoint xAPI a enfin un
appelant. La boucle complète du MVP — activité donnée, contenu joué, événement
capturé, lacune et score recalculés, tableau de bord mis à jour — a été jouée de
bout en bout sur la pile vivante.

### Phase 9 bis, travaux hors étape du 17 août 2026

Menés après la clôture de l’étape 13, sur autorisation permanente du
propriétaire, parce qu’ils bloquaient l’usage réel de la plateforme plutôt qu’une
étape à venir.

| ID | Travail | Dépendances | Statut | Preuve |
|---|---|---|---|---|
| HORS-01 | Examen d’initiation | DASH-04 | Terminé | Douze questions, une par compétence, donnée par la plateforme ; la bonne réponse ne quitte pas le serveur |
| HORS-02 | Rendre la création de comptes possible | HORS-01 | Terminé | Quatre pages d’authentification distinctes ; le remplissage automatique fonctionne au lieu d’être désactivé |
| HORS-03 | Identité visuelle « le cahier » | HORS-02 | Terminé | Le rouge réservé aux pannes, le fil de prérequis, contrastes AA vérifiés, PR #41 |
| HORS-04 | Fiches de remédiation | HORS-03 | Terminé | Douze fiches écrites ici, ADR-017 |
| HORS-05 | Ouvrir le catalogue H5P | HORS-04 | Terminé | ADR-012 amendée à huit types, migration 0015, commande `libraries`, 1135 tests |
| HORS-06 | Rendre la démonstration montrable | HORS-05 | Terminé | Recette par tunnel ; `PUBLIC_HOST` sans quoi toute connexion échouerait derrière un tunnel |

`HORS-01` referme la première flèche du MVP, qui n’avait jamais été construite :
un enfant inscrit n’avait aucune compétence observée, donc aucun diagnostic.
`HORS-04` referme la dernière : les douze remédiations étaient des lignes de
catalogue sans rien derrière, et le diagnostic proposait des réparations qui
s’ouvraient sur une page vide.

L’examen et les fiches partagent leur correction et **pas** ce qu’ils répondent :
une fiche explique, l’examen se tait. Cette asymétrie a ouvert une faille — poster
ses réponses d’examen à la route des fiches — refermée par un contrôle de la
nature de l’activité. ADR-017 consigne l’ensemble.

### Prochaine tâche

Ouvrir l’étape 14, notifications. La page « Ce qui a changé » livrée par
`DASH-03` en est la présentation provisoire et devra s’y raccorder.
