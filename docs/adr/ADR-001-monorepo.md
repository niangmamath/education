# ADR-001 : Architecture Monorepo

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

Le projet StudentConnect nécessite une structure qui permette de gérer efficacement :

1. **Multiple applications** : Frontend (Next.js), Backend (FastAPI)
2. **Code partagé** : Schémas, types, utilitaires, configuration
3. **Infrastructure** : Docker, scripts, configurations CI/CD
4. **Documentation** : Architecture, API, guides utilisateur

### Problème à résoudre

Choisir entre une architecture **monorepo** (un seul dépôt) ou **polyrepo** (plusieurs dépôts) pour organiser le code.

### Contraintes

- Équipe de taille limitée (développement en stage)
- Besoin de **partage de code** entre frontend et backend
- **Déploiement coordonné** des différentes parties
- **Maintenance simplifiée** de l'infrastructure
- **Visibilité** sur l'ensemble du projet

---

## Décision

**Adopter une architecture Monorepo** avec la structure suivante :

```
studentconnect/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── ui/                  # Composants partagés
│   ├── schemas/            # Schémas Pydantic/Zod
│   └── config/             # Configuration commune
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── scripts/
├── docs/
│   ├── architecture/
│   ├── adr/
│   └── user-guide/
└── steps/
```

### Outils de gestion

- **Gestionnaire de paquets** : pnpm (recommandé pour les monorepos)
- **Orchestrateur** : Turborepo (pour le caching et l'exécution optimisée)
- **Workspace** : Native support via pnpm/yarn/npm

---

## Options considérées

### 1. Monorepo

**Pour** :
- ✅ **Partage de code facile** entre frontend et backend
- ✅ **Dépendances unifiées** - une seule version de chaque bibliothèque
- ✅ **CI/CD simplifiée** - un seul pipeline pour tout le projet
- ✅ **Visibilité globale** - facile de voir l'impact des changements
- ✅ **Refactoring cross-cutting** - modifications cohérentes
- ✅ **Déploiement coordonné** - toutes les parties sont synchronisées
- ✅ **Onboarding plus simple** - tout est au même endroit

**Contre** :
- ❌ **Taille du dépôt** - peut devenir très grand
- ❌ **Build plus long** - tout doit être built ensemble
- ❌ **Permissions Git** - tous les contributeurs ont accès à tout
- ❌ **Complexité initiale** - configuration plus complexe

**Verdict** : ✅ **Sélectionné** - Les avantages l'emportent largement pour ce projet

---

### 2. Polyrepo (Multiple dépôts)

**Pour** :
- ✅ **Isolation des équipes** - permissions fines par dépôt
- ✅ **Déploiement indépendant** - chaque service peut être déployé séparément
- ✅ **Taille réduite** - chaque dépôt reste petit
- ✅ **Technologies différentes** - chaque dépôt peut utiliser sa stack

**Contre** :
- ❌ **Duplication de code** - code partagé doit être copié ou publié
- ❌ **Gestion des dépendances complexe** - versions à synchroniser
- ❌ **CI/CD complexe** - coordination entre dépôts
- ❌ **Visibilité réduite** - difficile de voir l'impact global
- ❌ **Refactoring difficile** - changements cross-dépôt complexes
- ❌ **Onboarding plus complexe** - plusieurs dépôts à cloner

**Verdict** : ❌ **Rejeté** - Ne convient pas pour une petite équipe avec besoin de partage de code

---

### 3. Hybrid (Monorepo + Polyrepo)

**Pour** :
- ✅ Combine les avantages des deux approches
- ✅ Permet l'isolation quand nécessaire

**Contre** :
- ❌ **Complexité maximale**
- ❌ **Difficile à maintenir** pour une petite équipe
- ❌ **Sur-ingénierie** pour ce projet

**Verdict** : ❌ **Rejeté** - Trop complexe pour les besoins actuels

---

## Conséquences

### Conséquences positives

- **Productivité accrue** : Partage de code sans duplication
- **Cohérence** : Toutes les parties du projet utilisent les mêmes versions
- **Simplicité de développement** : Une seule commande pour installer les dépendances
- **Meilleure collaboration** : Tous les développeurs voient tout le code
- **Refactoring facilité** : Les changements cross-cutting sont plus simples

### Conséquences négatives

- **Configuration initiale plus complexe**
- **Taille du dépôt peut croître** rapidement
- **Tous les tests tournent ensemble** (peut être long)
- **Accès complet pour tous** les développeurs

### Mitigations

- **Utiliser Turborepo** pour le caching et l'exécution sélective
- **Structure claire** des dossiers pour éviter la confusion
- **Script de build optimisés** pour ne builder que ce qui a changé
- **.gitignore bien configuré** pour exclure les fichiers inutiles

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Taille du dépôt trop grande | Moyenne | Élevé | Nettoyage régulier, .gitignore efficace |
| Build trop long | Faible | Moyen | Turborepo, caching agressif |
| Complexité de configuration | Élevée | Moyen | Documentation détaillée, scripts d'installation |
| Conflits de merge fréquents | Moyenne | Moyen | Bonnes conventions de commit, reviews attentives |

---

## Validation

### Compatibilité avec les outils

| Outil | Support Monorepo | Notes |
|-------|-----------------|-------|
| pnpm | ✅ Excellent | Workspaces natifs |
| yarn | ✅ Bon | Workspaces natifs |
| npm | ⚠️ Limité | Workspaces depuis v7 |
| Turborepo | ✅ Excellent | Conçu pour monorepos |
| Docker | ✅ Bon | Multi-stage builds |
| GitHub Actions | ✅ Bon | Matrix builds |

### Expérience de l'équipe

L'équipe a de l'expérience avec les monorepos (AgriConnect), ce qui réduit le risque de configuration.

---

## Implémentation

### Structure initiale

```bash
studentconnect/
├── apps/
│   ├── web/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   └── api/
│       ├── requirements.txt
│       ├── pyproject.toml
│       └── src/
├── packages/
│   ├── ui/
│   │   └── package.json
│   ├── schemas/
│   │   └── package.json
│   └── config/
│       └── package.json
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile.web
│   │   └── Dockerfile.api
│   └── scripts/
├── docs/
├── steps/
├── pnpm-workspace.yaml
└── package.json (racine)
```

### Configuration de base

1. **pnpm-workspace.yaml** :
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

2. **package.json (racine)** : Scripts globaux

3. **Turborepo** : Pour le caching et l'orchestration

---

## Références

- [Monorepo.tools](https://monorepo.tools/) - Ressources complètes sur les monorepos
- [Turborepo Documentation](https://turbo.build/repo)
- [pnpm Workspaces](https://pnpm.io/workspaces)
- [Why Monorepos?](https://sematext.com/blog/why-monorepos/)
- [Monorepo vs Polyrepo](https://medium.com/@mattkleinhorst/monorepos-vs-polyrepos-35f329156fa7)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Comparaison Monorepo vs Polyrepo

| Critère | Monorepo | Polyrepo |
|---------|----------|----------|
| Partage de code | ✅ Facile | ❌ Difficile |
| Gestion des dépendances | ✅ Simple | ❌ Complexe |
| CI/CD | ✅ Simplifiée | ❌ Complexe |
| Isolation | ❌ Limitée | ✅ Bonne |
| Taille du dépôt | ❌ Grande | ✅ Petite |
| Onboarding | ✅ Simple | ❌ Complexe |
| Déploiement | ✅ Coordonné | ⚠️ Indépendant |
| Permissions | ❌ Globales | ✅ Fines |

### Recommandations supplémentaires

1. **Commencer simple** : Ne pas sur-ingénier la structure
2. **Documenter** : Bien documenter la structure et les scripts
3. **Automatiser** : Scripts pour les tâches courantes (install, build, test)
4. **Surveiller** : Suivre la taille du dépôt et les performances de build
