# StudentConnect Workspace Configuration

> Configuration du monorepo avec pnpm et Turborepo

## Structure

```
studentconnect/
├── apps/
│   ├── web/          # Next.js 16 Frontend
│   └── api/          # FastAPI Backend
├── packages/
│   ├── ui/           # Composants partagés (Radix UI, Lucide)
│   ├── schemas/      # Schémas Pydantic/Zod partagés
│   └── config/       # Configuration commune
├── infrastructure/
│   ├── docker/       # Docker Compose, Dockerfiles
│   ├── nginx/        # Configuration NGINX
│   └── scripts/      # Scripts utilitaires
├── docs/
│   ├── architecture/
│   ├── adr/
│   └── ...
├── package.json      # Root package.json
├── pnpm-workspace.yaml
├── turbo.json        # Turborepo configuration
└── ...
```

## Gestionnaire de paquets

- **pnpm** v11.21.0 - Gestionnaire de paquets Node.js
- Justification : Efficace pour les monorepos, économise de l'espace disque, gestion native des workspaces

## Workspace Configuration

### pnpm-workspace.yaml

```yaml
apps:
  - "apps/*"
packages:
  - "packages/*"
```

### Scripts racine disponibles

| Script | Description |
|--------|-------------|
| `pnpm dev` | Démarre tous les services en mode développement |
| `pnpm dev:web` | Démarre uniquement le frontend Next.js |
| `pnpm dev:api` | Démarre uniquement le backend FastAPI |
| `pnpm build` | Build tous les packages |
| `pnpm lint` | Exécute le linting sur tous les packages |
| `pnpm typecheck` | Vérifie les types TypeScript |
| `pnpm test` | Exécute tous les tests |
| `pnpm format` | Formate le code |
| `pnpm clean` | Nettoie les builds et caches |
| `pnpm install:all` | Installe toutes les dépendances |

### Turborepo

- **Version** : ^2.3.0
- **Fonctionnalités** : Cache partagé, exécution parallèle, dépendances entre tâches
- **Configuration** : Voir `turbo.json`

#### Tâches Turborepo

- `build` : Construit tous les packages avec dépendances
- `dev` : Mode développement (non caché)
- `lint` : Linting du code
- `typecheck` : Vérification des types
- `test` : Exécution des tests (dépend de build)
- `format` : Formatage du code
- `clean` : Nettoyage des artefacts
- `db:migrate`, `db:upgrade` : Gestion des migrations

## Commandes utiles

```bash
# Installer toutes les dépendances
pnpm install --recursive

# Installer dans un package spécifique
pnpm --filter apps/web add next

# Lister tous les packages du workspace
pnpm ls --depth -1

# Exécuter un script dans un package
pnpm --filter apps/web dev

# Exécuter avec turbo
npx turbo run build

# Voir le graphe de dépendances
pnpm ls --graph
```

## Politiques

- Tous les packages doivent être dans `apps/` ou `packages/`
- Les dépendances externes doivent être déclarées dans le package concerné
- Les dépendances partagées doivent être dans `packages/`
- Aucune dépendance circulaire autorisée

## Fichiers de configuration

- `package.json` - Root package avec scripts
- `pnpm-workspace.yaml` - Définition des workspaces
- `turbo.json` - Configuration Turborepo
- `.gitignore` - Exclusions git

*Dernière mise à jour : 10 août 2026*
