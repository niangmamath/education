# Audit initial du dépôt StudentConnect

**Date :** 2026-08-07  
**Branche auditée :** `main` (commit `63d5720`)  
**Périmètre :** inventaire complet, sécurité, écarts avec le cahier des charges technique et structure cible.

---

## 1. Synthèse exécutive

Le dépôt `StudentConnect` est au stade **pré-implémentation**. Il contient une feuille de route agentique (`steps/`), un README minimal, un fichier HTML de test d’embed CK-12 et une archive `steps.zip`. **Aucun code applicatif Django**, aucune configuration Docker, CI, ni documentation technique dans `docs/` n’était présente avant cet audit.

Les décisions produit et stack documentées dans `steps/etat.md` et `steps/PROMPT_GENERAL.md` sont cohérentes entre elles, mais **non matérialisées** dans le dépôt. L’étape `02_socle_technique` est le prochain jalon critique.

| Indicateur | État |
|---|---|
| Code métier | Absent |
| Stack Django/DRF | Non initialisée |
| PostgreSQL / Docker | Absent |
| CI GitHub Actions | Absente |
| ADR / architecture | Créés par l’étape 01 (cette livraison) |
| Secrets commités | Aucun détecté |
| Données réelles d’enfant | Aucune détectée |

---

## 2. État Git

| Élément | Valeur |
|---|---|
| Branche active | `main` |
| Remote | `origin/main` (à jour) |
| Historique | 2 commits |
| Working tree | Propre |

### Commits récents

| Hash | Message |
|---|---|
| `63d5720` | Ajouter la feuille de route StudentConnect en 13 phases. |
| `f10ac9a` | first commit |

### Branches

- Locale : `main`
- Distante : `origin/main`, `origin/HEAD → origin/main`
- Aucune branche de fonctionnalité active.

---

## 3. Arborescence réelle (2026-08-07)

```text
StudentConnect/
├── index.html              # Test embed CK-12 (hors stack cible)
├── README.md               # Titre seul (« # StudentConnect »)
├── steps/                  # Feuille de route, prompts agents, etat.md
│   ├── 01_gouvernance_et_audit/ … 13_documentation_et_livraison/
│   ├── etat.md
│   ├── MANIFESTE.md
│   ├── MODELE_RAPPORT.md
│   ├── PROMPT_GENERAL.md
│   └── README.md
└── steps.zip               # Archive du dossier steps/
```

**Absent par rapport à la structure cible** (`steps/PROMPT_GENERAL.md` §8) :

- `config/`, `apps/`, `templates/`, `static/`, `fixtures/`, `tests/`
- `docs/` (avant livraison étape 01)
- `docker-compose.yml`, `pyproject.toml`, `.env.example`
- `.gitignore`, `.github/`, `CONTRIBUTING.md`, `LICENSE`

---

## 4. Stack et dépendances

| Composant attendu (V0.1) | Présent dans le dépôt | Version observée |
|---|---|---|
| Python 3.12 | Non | — |
| Django 5.x | Non | — |
| DRF | Non | — |
| Bootstrap 5 | Non | — |
| HTMX | Non | — |
| PostgreSQL | Non | — |
| pytest / coverage | Non | — |
| Ruff / Black / djLint | Non | — |
| Docker Compose | Non | — |
| GitHub Actions | Non | — |

**Constat :** la stack est entièrement **documentée** dans `steps/PROMPT_GENERAL.md` et `steps/etat.md`, sans manifeste de dépendances (`pyproject.toml`, `requirements.txt`).

---

## 5. Fichiers de configuration et gouvernance

| Fichier | Présent | Commentaire |
|---|---|---|
| `README.md` | Oui | Insuffisant pour onboarding |
| `.gitignore` | Non | **Risque P0** avant tout commit de code |
| `.env` / `.env.example` | Non | Attendu à l’étape 02 |
| `LICENSE` | Non | Statut juridique non défini |
| `.github/` | Non | Templates et CI à créer (étape 01.3) |
| `CONTRIBUTING.md` | Non | À créer (étape 01.3) |

---

## 6. Vérification sécurité et données sensibles

### Recherches effectuées

- Fichiers `.env*` : aucun
- Motifs `api_key`, `secret`, `password`, `token`, clés privées : aucune occurrence sensible hors documentation des prompts
- Bases de données locales (`.sqlite3`, `.db`) : aucune
- Fichiers de credentials JSON : aucun

### `index.html`

- Contient un iframe CK-12 public (`//www.ck12.org/assessment/ui/embed.html?...`).
- Aucun identifiant personnel, cookie ou jeton d’authentification.
- HTML structurellement incorrect (`<head>` imbriqué dans `<body>`) — dette mineure, hors périmètre métier.

### Conclusion sécurité

**Aucun secret ni donnée réelle d’enfant détectée** dans le dépôt au moment de l’audit.

---

## 7. GitHub (dépôt distant)

| Élément | État |
|---|---|
| Organisation | `Tidianesarrndiaye-org` |
| Dépôt | `StudentConnect` |
| URL | https://github.com/Tidianesarrndiaye-org/StudentConnect |
| Description | Vide |
| Issues ouvertes | Aucune (au moment de l’audit) |
| Labels | Labels GitHub par défaut uniquement |
| GitHub Project | Documenté dans `etat.md` ; **non vérifiable** via CLI (scope `read:project` manquant) |

---

## 8. Documenté versus réel

| Domaine | Documenté (`etat.md`, prompts) | Réel dans le dépôt | Écart |
|---|---|---|---|
| Architecture monolithe Django | Oui | Non implémentée | Majeur |
| Bootstrap 5 (pas Tailwind) | Décision validée | Aucun front | Majeur |
| PostgreSQL | Décision validée | Absent | Majeur |
| H5P POC | Piste principale | Absent | Attendu (étape 04) |
| CK-12 / Khan / PhET | Stratégie définie | Seul `index.html` CK-12 | Partiel |
| Kolibri spike | Non bloquant | Absent | Attendu (étape 12) |
| Cahiers des charges V1/V2 | Marqués terminés | **Non présents** dans le dépôt | Documentation externe |
| GitHub Project configuré | Marqué terminé | Partiellement vérifiable | À confirmer manuellement |
| Feuille de route 13 phases | — | `steps/` complet | Aligné |
| Prototype V0.1 | Cible | 0 % code | Normal à ce stade |

---

## 9. Risques classés P0 à P3

| ID | Priorité | Risque | Mitigation recommandée |
|---|---|---|---|
| R-01 | **P0** | Absence de `.gitignore` avant développement | Créer à l’étape `02_socle_technique` (ou immédiatement) |
| R-02 | **P0** | Retard sur le socle technique avec deadline stage (4 sept. 2026) | Enchaîner `02_socle_technique` sans délai |
| R-03 | **P1** | README et docs produit absents du dépôt | Importer ou lier les cahiers des charges ; enrichir README |
| R-04 | **P1** | Pas de CI : régressions non détectées | Mettre en place GitHub Actions à l’étape 02.3 |
| R-05 | **P1** | Hébergement H5P non tranché | ADR-004 en statut `Proposed` pour le mode d’hébergement |
| R-06 | **P1** | Référentiel pilote (programme, matières, compétences) ouvert | Bloquer avant étape 03 si non validé |
| R-07 | **P2** | `steps.zip` duplique `steps/` | Supprimer ou documenter l’usage ; éviter divergence |
| R-08 | **P2** | Absence de LICENSE | Choisir licence (ex. MIT ou propriétaire stage) |
| R-09 | **P2** | GitHub Project non vérifiable par agent | Checklist manuelle étape 01.3 |
| R-10 | **P2** | Intégrations CK-12/Khan sans API officielle | Stratégie `launch-only` / wrapper déjà documentée |
| R-11 | **P3** | `index.html` HTML invalide | Corriger ou déplacer vers `docs/spikes/` à l’étape 04 |
| R-12 | **P3** | Périmètre 11 modules vs durée stage | Respecter flux vertical V0.1 uniquement |

---

## 10. Proposition d’arborescence cible compatible avec l’existant

Principe : **ne pas déplacer** `steps/` ni `index.html` sans décision ADR ; ajouter la structure applicative en parallèle.

```text
StudentConnect/
├── config/                     # settings, urls, wsgi — NEW
├── apps/
│   ├── accounts/               # M01
│   ├── students/               # M02
│   ├── competencies/           # M03
│   ├── resources/              # M04
│   ├── learning/               # M05
│   ├── assessments/            # M06
│   ├── gaps/                   # M07
│   ├── remediation/            # M08
│   ├── dashboards/             # M09–M10
│   └── audit/                  # M11
├── templates/
├── static/
├── fixtures/
├── docs/
│   ├── architecture/           # audit-initial.md, decision-register.md
│   ├── adr/                    # ADR-001 … ADR-007
│   ├── api/
│   └── user-guide/
├── tests/
├── steps/                      # CONSERVER — gouvernance agents
├── index.html                  # CONSERVER — spike CK-12 (renommer/déplacer plus tard)
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── .gitignore
├── .github/
├── CONTRIBUTING.md
└── README.md                   # ENRICHIR
```

### Mapping modules → apps Django

| Module | App Django | Priorité V0.1 |
|---|---|---|
| M01 Comptes, famille | `accounts` | Haute (étape 06) |
| M02 Profil, dossier | `students` | Haute |
| M03 Référentiel | `competencies` | Haute (étape 03) |
| M04 Catalogue | `resources` | Haute (étape 04) |
| M05 Parcours | `learning` | Moyenne |
| M06 Évaluations | `assessments` | Haute (étape 07) |
| M07 Lacunes | `gaps` | Haute (étape 08) |
| M08 Remédiation | `remediation` | Haute (étape 09) |
| M09–M10 Dashboards | `dashboards` | Moyenne (étape 10) |
| M11 Admin, audit | `audit` | Basse (étape 10–11) |

---

## 11. Recommandations immédiates

1. **Exécuter `02_socle_technique`** : Django, PostgreSQL, Docker, `.gitignore`, `.env.example`, CI.
2. **Conserver `steps/`** comme source de vérité agentique ; mettre à jour `etat.md` après chaque étape.
3. **Valider le référentiel pilote** (programme, classe, 3 matières, 10–20 compétences) avant l’étape 03.
4. **Trancher l’hébergement H5P** (ADR-004) avant le spike de l’étape 04.
5. **Importer ou lier** les cahiers des charges fonctionnels/techniques dans `docs/` ou wiki GitHub.
6. **Enrichir le README** racine avec vision, stack, prérequis et lien vers `docs/architecture/`.
7. **Exécuter `gh auth refresh -s read:project`** pour permettre l’audit GitHub Project par les agents.

---

## 12. Critères d’acceptation de l’audit

- [x] Inventaire complet de l’arborescence et de Git
- [x] Stack et versions identifiées (documentées vs absentes)
- [x] Recherche secrets et données sensibles sans exposition
- [x] Risques classés P0 à P3
- [x] Écarts documentés par rapport à la structure cible
- [x] Proposition d’arborescence compatible avec l’existant
- [x] Aucun fichier supprimé ni déplacé pendant l’audit
