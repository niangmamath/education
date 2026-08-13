# Migration de Tailwind vers Bootstrap

## Audit constaté

Le frontend utilise actuellement Tailwind CSS 4 :

- `tailwindcss` et `@tailwindcss/postcss` sont des dépendances de développement ;
- `apps/web/app/globals.css` importe `tailwindcss` ;
- `apps/web/postcss.config.mjs` active le plugin Tailwind ;
- `layout.tsx`, `page.tsx` et `health/page.tsx` contiennent de nombreuses classes utilitaires Tailwind ;
- Bootstrap, React Bootstrap et Popper ne sont pas installés ;
- aucun dossier `components` n'existe encore.

La migration ne peut donc pas se limiter à remplacer l'import CSS : cela rendrait les pages actuelles non stylées.

## Version cible

- Bootstrap : `5.3.8`, version exacte ;
- React Bootstrap : non retenu initialement ;
- Popper : non ajouté tant qu'aucun dropdown, tooltip, popover ou composant équivalent n'en a besoin ;
- chargement local via le paquet npm, aucun CDN.

## Stratégie en quatre commits

### Commit A, audit et contrat visuel

- versionner le présent audit ;
- définir tokens, composants et critères d'accessibilité ;
- ne modifier aucune dépendance.

### Commit B, installer Bootstrap et migrer la page publique

- ajouter `bootstrap@5.3.8` comme dépendance exacte ;
- importer le CSS compilé localement ;
- créer les variables StudentConnect dans `globals.css` ;
- réécrire `app/page.tsx` sans classes Tailwind ;
- conserver temporairement Tailwind uniquement pour `/health` si nécessaire ;
- documenter explicitement la coexistence temporaire.

### Commit C, migrer la page Health

- remplacer toutes les classes Tailwind de `app/health/page.tsx` ;
- préserver les états healthy, degraded, unhealthy et loading ;
- vérifier les textes, icônes et contrastes ;
- supprimer la dernière dépendance fonctionnelle aux utilitaires Tailwind.

### Commit D, retirer Tailwind

Seulement lorsque la recherche ne retourne plus de classes ou d'import Tailwind :

- supprimer `tailwindcss` et `@tailwindcss/postcss` ;
- retirer le plugin de `postcss.config.mjs` ou supprimer PostCSS s'il n'est plus requis ;
- supprimer `@import "tailwindcss"` ;
- régénérer le lockfile ;
- exécuter tous les contrôles.

## Coexistence temporaire

Bootstrap et Tailwind appliquent tous deux des styles de base. Une coexistence prolongée peut provoquer des différences sur les boutons, formulaires, titres et espacements. La période hybride doit donc rester courte, documentée et couverte par des vérifications visuelles.

Pendant cette période :

- ne pas mélanger les classes Bootstrap et Tailwind sur un même composant ;
- utiliser un composant entièrement migré ou entièrement hérité ;
- surveiller les styles de base ;
- ne pas créer de nouvelle classe Tailwind ;
- ne pas utiliser `!important` pour masquer les collisions.

## Inventaire des fichiers à migrer

```text
apps/web/app/layout.tsx
apps/web/app/page.tsx
apps/web/app/health/page.tsx
apps/web/app/globals.css
apps/web/postcss.config.mjs
apps/web/package.json
pnpm-lock.yaml
```

`next-env.d.ts` ne doit pas être modifié volontairement. Toute modification générée par Next.js doit être examinée puis restaurée si elle n'appartient pas au changement.

## Commandes de contrôle

```bash
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
NEXT_TELEMETRY_DISABLED=1 pnpm --filter @studentconnect/web run build
git diff --check
```

Contrôle de retrait final :

```bash
grep -RInE 'tailwind|@tailwindcss|@import "tailwindcss"' apps/web --exclude-dir=node_modules --exclude-dir=.next
```

## Rollback

Chaque phase doit être un commit autonome. En cas de régression :

1. ne pas corriger sur `main` ;
2. identifier le commit de migration concerné ;
3. restaurer le dernier état vert ;
4. conserver l'audit et les preuves ;
5. reprendre avec un périmètre plus petit.

## Décision

La migration est faisable mais doit être progressive. La prochaine opération sera le commit B : installation exacte de Bootstrap et migration de la page publique, sans suppression immédiate de Tailwind.
