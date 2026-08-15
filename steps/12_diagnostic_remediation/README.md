# Étape 12, diagnostic remediation

## Objectif

Produire des diagnostics explicables et des recommandations de remédiation.

## Sous-étapes

1. `01_regles_diagnostic.md` : Règles de diagnostic
2. `02_moteur_recommandation.md` : Remédiation
3. `03_api_diagnostic.md` : API diagnostic
4. `04_cloturer_etape.md` : Clôture diagnostic

## Conditions de clôture

- migrations upgrade et downgrade validées si applicables ;
- Ruff, Mypy et Pytest verts ;
- TypeScript, ESLint et build Next.js verts si le web est modifié ;
- contrôles d’autorisation et d’isolation validés ;
- documentation et preuves produites ;
- commit et push ;
- CI distante applicable réussie ;
- fusion contrôlée vers `main` ;
- ETAT et PLANNING mis à jour après preuves.
