# 05.7, clôturer l’étape

## Contrôles obligatoires

```bash
git status --short
git diff --check
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
NEXT_TELEMETRY_DISABLED=1 pnpm --filter @studentconnect/web run build
```

Exécuter les tests ajoutés pour les composants et la navigation.

## Rapports à produire après les tests

- parcours et routes ;
- design system Bootstrap ;
- layout Parent ;
- layout Élève ;
- accessibilité et responsive ;
- rapport de clôture.

## Clôture

L’étape ne passe à Terminé qu’après :

- preuves réelles ;
- contrôles verts ;
- mise à jour d’`ETAT.md` et `PLANNING.md` ;
- commit et push ;
- validation GitHub Actions ;
- fusion contrôlée vers `main`.
