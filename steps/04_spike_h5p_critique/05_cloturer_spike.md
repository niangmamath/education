# 04.5, clôturer le spike

## Objectif

Clôturer l’étape uniquement à partir des preuves réelles.

## Contrôles obligatoires

```bash
git status --short
git diff --check
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
NEXT_TELEMETRY_DISABLED=1 pnpm --filter @studentconnect/web run build
```

Exécuter également les tests propres au spike et vérifier qu’aucun paquet H5P non autorisé n’est indexé.

## Rapports à produire après les essais

- rapport protocole et paquets ;
- rapport lecture Standalone ;
- rapport capture xAPI ;
- rapport compatibilité et sécurité ;
- rapport de clôture.

## Décision finale

Le rapport doit conclure par une seule décision :

1. poursuivre avec les types listés ;
2. poursuivre sous conditions et traiter les blocages ;
3. abandonner cette approche et ouvrir une nouvelle décision d’architecture.

## Suivi

Après validation :

- mettre à jour l’ADR H5P ;
- mettre `P0-06` à Terminé ;
- mettre `P0-07` en cours ou à faire selon la décision ;
- créer le commit ;
- pousser la branche ;
- contrôler GitHub Actions ;
- fusionner seulement après validation.
