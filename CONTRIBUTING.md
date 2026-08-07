# Contribuer à StudentConnect

Plateforme familiale de suivi et remédiation de l'élève — prototype V0.1 (stage Casablanca 2026).

## Avant de commencer

1. Lire `steps/etat.md` et `steps/PROMPT_GENERAL.md`.
2. Vérifier les ADR dans `docs/adr/` et le registre `docs/architecture/decision-register.md`.
3. Travailler sur une branche courte : `feat/M03-carte-competences`, `fix/M06-score`, `docs/api`.

## Règles non négociables

- **Données fictives uniquement** — aucune donnée réelle d'enfant.
- **Aucun secret** dans le dépôt (`.env`, tokens, mots de passe).
- **Bootstrap 5 + HTMX** — pas Tailwind CSS (ADR-002).
- **Monolithe Django modulaire** (ADR-001).
- Une note ne remplace jamais une compétence ; l'historique n'est jamais écrasé.

## Workflow Git

```text
main (protégée) ← pull request ← feat/xxx ou fix/xxx
```

### Commits

Format : `feat(M03): add competency history`

### Pull requests

- Lier une issue GitHub.
- Remplir le template PR (`.github/pull_request_template.md`).
- Une fonctionnalité significative = une PR reviewable.

## GitHub Project

Statuts : `Backlog`, `Ready`, `In progress`, `In review`, `Blocked`, `Done`.

Priorités : `P0 Critical`, `P1 High`, `P2 Medium`, `P3 Low`.

Itérations : I0 (5–11 août), I1 (12–18), I2 (19–25), I3 (26 août – 4 sept.).

## Développement local

> À compléter après l'étape `02_socle_technique` (Docker Compose, pytest, etc.).

## Agents et feuille de route

Les prompts par étape sont dans `steps/`. Chaque réalisation produit un rapport `rapport_YYYY-MM-DD_HHMM_<slug>.md` dans le dossier de l'étape.

## Questions

Ouvrir une issue avec le template **Decision** pour les choix d'architecture non couverts par un ADR existant.
