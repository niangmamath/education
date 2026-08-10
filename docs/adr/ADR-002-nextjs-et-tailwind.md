# ADR-002 : Next.js 16 et Tailwind CSS 4 pour le Frontend

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect nécessite un **frontend moderne, performant et réactif** pour offrir une expérience utilisateur optimale aux élèves de 6 à 11 ans et à leurs parents.

### Problème à résoudre

Choisir le **framework frontend** et la **solution de styling** qui répondent aux exigences suivantes :

1. **Expérience utilisateur** : Interface intuitive, visuelle et gamifiée
2. **Performance** : Chargement rapide, LCP < 2 secondes
3. **Maintenabilité** : Code propre, type-safe, facile à maintenir
4. **Écosystème** : bibliothèques riches et communauté active
5. **Compatibilité** : Travail avec FastAPI backend via REST
6. **Internationalisation** : Support multilingue (français, anglais)

### Contraintes

- Équipe familière avec React/TypeScript
- Besoin de **SSR/SSG** pour le SEO et la performance
- **Budget limité** - pas de licence payante
- **Deadline serré** - développement en stage
- **Design system** à construire rapidement

---

## Décision

**Adopter Next.js 16 avec App Router** comme framework frontend, associé à **Tailwind CSS 4** pour le styling.

### Stack Frontend Complète

```
Frontend Stack:
├── Framework: Next.js 16
├── Language: TypeScript (strict mode)
├── Router: App Router
├── Styling: Tailwind CSS 4
├── UI Components: Radix UI, Lucide React
├── Animations: Framer Motion
├── State: Zustand
├── Data Fetching: TanStack Query
├── Forms: React Hook Form + Zod
├── i18n: next-intl
├── Charts: Recharts
└── Testing: Vitest, Testing Library
```

---

## Options considérées

### 1. Next.js 16 + Tailwind CSS 4

**Pour** :
- ✅ **SSR/SSG natif** : Optimisé pour la performance et le SEO
- ✅ **App Router** : Nouvelle architecture moderne, meilleure DX
- ✅ **TypeScript first** : Intégration parfaite avec TypeScript
- ✅ **API Routes** : Peut héberger des endpoints API si nécessaire
- ✅ **Image Optimization** : Automatic image optimization
- ✅ **Tailwind CSS 4** : Utility-first, très productif, bonne communauté
- ✅ **Vercel Deployment** : Déploiement simplifié
- ✅ **Écosystème riche** : Nombreuses bibliothèques compatibles
- ✅ **Performance** : Excellente avec les optimisations automatiques
- ✅ **i18n** : Support natif via next-intl

**Contre** :
- ❌ Courbe d'apprentissage pour App Router (nouveau)
- ❌ Tailwind peut générer du HTML verbosité
- ❌ Moins de "boilerplate" peut être déroutant

**Verdict** : ✅ **Sélectionné** - Meilleur compromis pour nos besoins

---

### 2. Next.js 16 + Chakra UI / Mantine

**Pour** :
- ✅ Composants prêt-à-l'emploi
- ✅ Design system intégré
- ✅ Accessibilité built-in

**Contre** :
- ❌ Bundle size plus grand
- ❌ Moins de contrôle sur le design
- ❌ Thème personnalisation complexe
- ❌ Moins flexible pour un design custom

**Verdict** : ❌ **Rejeté** - Moins adapté pour un design system custom

---

### 3. Next.js 16 + Bootstrap

**Pour** :
- ✅ Très connu et documenté
- ✅ Composants prêts à l'emploi

**Contre** :
- ❌ **Interdit** par DECISIONS_FINALES.md (Choix exclus)
- ❌ Bundle size très grand
- ❌ Moins moderne
- ❌ Moins flexible
- ❌ Dépendances jQuery (dans certaines versions)

**Verdict** : ❌ **Rejeté** - Explicitement interdit + pas optimal

---

### 4. React + Vite + Tailwind

**Pour** :
- ✅ Plus léger que Next.js
- ✅ Build ultra-rapide avec Vite
- ✅ Flexibilité totale

**Contre** :
- ❌ Pas de SSR natif (moins bon pour SEO)
- ❌ Routing à configurer manuellement
- ❌ Moins d'optimisations automatiques
- ❌ API Routes manquantes
- ❌ Image optimization à gérer manuellement

**Verdict** : ❌ **Rejeté** - Le SSR et les optimisations de Next.js sont trop précieuses

---

### 5. Vue.js / Svelte

**Pour** :
- ✅ Frameworks modernes
- ✅ Bonne performance

**Contre** :
- ❌ Équipe pas familière avec ces technologies
- ❌ Courbe d'apprentissage
- ❌ Écosystème différent (pas compatible avec React)
- ❌ Moins de bibliothèques disponibles

**Verdict** : ❌ **Rejeté** - Risque trop élevé pour le timeline

---

### 6. Angular

**Pour** :
- ✅ Framework complet
- ✅ TypeScript natif
- ✅ Enterprise ready

**Contre** :
- ❌ Très lourd
- ❌ Courbe d'apprentissage abrupte
- ❌ Bundle size très grand
- ❌ Moins adapté pour un MVP rapide

**Verdict** : ❌ **Rejeté** - Trop lourd pour nos besoins

---

## Conséquences

### Conséquences positives

- **Développement rapide** : Hot reloading, excellente DX
- **Performance optimale** : SSR, optimisations images, code splitting
- **Type Safety** : TypeScript strict réduit les bugs
- **Maintenabilité** : Code structuré avec App Router
- **Flexibilité design** : Tailwind permet un design custom complet
- **Internationalisation** : Support natif via next-intl
- **Accessibilité** : Facile à implémenter avec Radix UI

### Conséquences négatives

- **Courbe d'apprentissage** pour App Router
- **Bundle size** peut être grand avec toutes les dépendances
- **Configuration initiale** plus complexe

### Mitigations

- **Documentation** : Bien documenter les conventions
- **Templates** : Créer des templates pour les pages et composants
- **Optimisation** : Utiliser dynamic imports pour réduire le bundle
- **Formation** : Session de formation sur Next.js 16 et App Router

---

## Validation

### Compatibilité avec les exigences

| Exigence | Next.js 16 + Tailwind | Score |
|----------|----------------------|-------|
| Performance (LCP < 2s) | ✅ Excellente | 10/10 |
| SSR/SSG | ✅ Natif | 10/10 |
| TypeScript | ✅ Premier classe | 10/10 |
| i18n | ✅ next-intl | 10/10 |
| Design System | ✅ Tailwind + Radix | 9/10 |
| Écosystème | ✅ Très riche | 10/10 |
| Déploiement | ✅ Simple (Vercel) | 10/10 |
| Maintenance | ✅ Bonne | 9/10 |

### Expérience de l'équipe

L'équipe a de l'expérience avec React et TypeScript, ce qui facilite l'adoption.

---

## Implémentation

### Structure du projet web/

```
apps/web/
├── app/
│   ├── [locale]/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/
│   │   │   ├── parent/
│   │   │   └── student/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── globals.css
│   └── layout.tsx (root)
├── components/
│   ├── ui/              # Composants Radix
│   ├── layouts/        # Layouts principaux
│   └── features/       # Composants par feature
├── lib/
│   ├── constants/
│   ├── hooks/
│   ├── utils/
│   └── types/
├── styles/
│   └── tailwind.css
├── public/
│   └── assets/
├── package.json
├── tsconfig.json
└── next.config.js
```

### Configuration de base

1. **next.config.js** : Configuration Next.js avec i18n, images, etc.
2. **tailwind.config.js** : Configuration Tailwind CSS 4
3. **tsconfig.json** : TypeScript strict
4. **package.json** : Dépendances et scripts

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| App Router trop nouveau | Moyenne | Moyen | Formation + Documentation |
| Bundle size trop grand | Faible | Moyen | Code splitting, lazy loading |
| Performance insuffisante | Faible | Élevé | Optimisations, tests de perf |
| Design incohérent | Moyenne | Moyen | Design system bien défini |

---

## Références

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js 16 New Features](https://nextjs.org/blog/next-16)
- [App Router Documentation](https://nextjs.org/docs/app)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS 4](https://tailwindcss.com/blog/tailwindcss-v4)
- [Radix UI](https://www.radix-ui.com/)
- [next-intl](https://next-intl-docs.vercel.app/)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Comparaison des frameworks

| Critère | Next.js | React+Vite | Vue | Svelte | Angular |
|---------|---------|------------|-----|--------|---------|
| SSR | ✅ | ❌ | ✅ | ❌ | ✅ |
| Performance | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| TypeScript | ✅ | ✅ | ✅ | ✅ | ✅ |
| Écosystème | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Courbe d'apprentissage | ⚠️ | ✅ | ⚠️ | ✅ | ❌ |
| Bundle Size | ⚠️ | ✅ | ✅ | ✅ | ❌ |
| Flexibilité | ✅ | ✅ | ✅ | ✅ | ❌ |

### Recommandations supplémentaires

1. **Utiliser les Server Components** pour optimiser les performances
2. **Créer un design system** avec Tailwind et Radix UI
3. **Implémenter le dark mode** pour une meilleure UX
4. **Optimiser les images** avec next/image
5. **Utiliser des fonts variables** pour réduire le poids
6. **Lazy load** les bibliothèques lourdes (Recharts)
