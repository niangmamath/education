# ADR-002 : Bootstrap 5 et HTMX, pas Tailwind CSS

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

L’interface doit être utilisable par des enfants du primaire et leurs parents, avec un délai court et une équipe sans spécialisation front-end lourde. Un choix initial Tailwind CSS avait été envisagé puis **explicitement abandonné** (`steps/etat.md`).

## Décision

Utiliser **Bootstrap 5** pour le design system et les composants UI, complété par **HTMX** et JavaScript natif pour les interactions légères (fragments, formulaires, mises à jour partielles). **Ne pas utiliser Tailwind CSS** ni un framework SPA pour la V0.1.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **Bootstrap 5 + HTMX** (retenue) | Composants prêts, accessibilité de base, intégration Django Templates, courbe d’apprentissage faible | Personnalisation visuelle limitée, dépendance CDN ou bundle |
| Tailwind CSS | Utility-first, design sur mesure | Abandonné ; courbe d’apprentissage, build pipeline |
| React / Vue SPA | Interactivité riche | Hors délai, double stack, SEO et simplicité parent/enfant |
| Bulma / Foundation | Alternatives CSS | Moins d’écosystème EdTech, pas de décision préalable |

## Conséquences

- Templates Django servent le HTML ; HTMX gère les échanges partiels sans API JSON obligatoire.
- Le design system est documenté à l’étape `05_ux_et_parcours`.
- djLint valide les templates ; pas de configuration PostCSS/Tailwind.
- Les maquettes et wireframes utilisent les composants Bootstrap (grille, cards, modals, navbar).

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Interface générique « Bootstrap-like » | P2 | Palette et composants customisés dans le design system |
| HTMX mal maîtrisé | P3 | Limiter aux cas simples ; tests manuels mobile |
| Réintroduction silencieuse de Tailwind | P2 | Revue de PR, pas de `tailwind.config` dans le dépôt |

## Références

- `steps/etat.md` — « Bootstrap 5 remplace Tailwind CSS »
- `steps/05_ux_et_parcours/01_concevoir_design_system_bootstrap.md`
