# Contributing to StudentConnect

> **Merci de vouloir contribuer à StudentConnect !**

Ce guide décrit comment contribuer au projet de manière efficace et respectueuse.

---

## Code of Conduct

En participant à ce projet, vous acceptez de respecter notre [Code of Conduct](CODE_OF_CONDUCT.md). Veuillez le lire avant de contribuer.

---

## Types de Contributions

Nous acceptons les contributions sous plusieurs formes :

- 🐛 **Bug Reports** - Signaler des bugs via les Issues GitHub
- 💡 **Feature Requests** - Proposer de nouvelles fonctionnalités
- 📝 **Documentation** - Améliorer la documentation existante
- 🔧 **Code** - Soumettre des Pull Requests
- 🎨 **Design** - Propositions de design et d'UX
- 🧪 **Testing** - Ajouter ou améliorer des tests
- ⚡ **Performance** - Optimisations
- 🔒 **Security** - Rapports de vulnérabilités (voir [SECURITY.md](SECURITY.md))

---

## Prérequis

### Connaissances requises

- **Frontend** : Next.js 16, React, TypeScript, Tailwind CSS 4
- **Backend** : FastAPI, Python 3.11+, SQLAlchemy 2, PostgreSQL
- **DevOps** : Docker, Docker Compose, GitHub Actions
- **Testing** : Pytest, Vitest, Playwright
- **Architecture** : Monorepo, modular monolith

### Environnement de développement

Voir [README.md](README.md) pour les prérequis et l'installation.

---

## Workflow de Contribution

### 1. Trouver une tâche

- Consulter [PLANNING.md](steps/PLANNING.md) pour les tâches à faire
- Vérifier les issues ouvertes sur GitHub
- Rejoindre la discussion dans les issues existantes avant de commencer

### 2. S'assigner une tâche

- **Pour les contributeurs externes** : Commenter sur l'issue pour s'assigner
- **Pour les membres de l'équipe** : S'assigner directement via GitHub

### 3. Créer une branche

```bash
# Mettre à jour le dépôt local
git checkout main
git pull origin main

# Créer une nouvelle branche pour votre contribution
git checkout -b feat/nom-de-la-fonctionnalite
git checkout -b fix/nom-du-bug
git checkout -b docs/amelioration-documentation
```

**Nomenclature des branches** :
- `feat/` - Nouvelle fonctionnalité
- `fix/` - Correction de bug
- `docs/` - Documentation
- `refactor/` - Refactoring de code
- `perf/` - Optimisation de performance
- `test/` - Ajout ou correction de tests
- `chore/` - Tâches de maintenance

### 4. Développer

- Suivre les [Conventions de Code](#conventions-de-code)
- Respecter l'architecture définie dans [DECISIONS_FINALES.md](steps/DECISIONS_FINALES.md)
- Écrire des tests pour les nouvelles fonctionnalités
- Documenter les changements

### 5. Commiter

```bash
# Ajouter les fichiers modifiés
git add .

# Créer un commit avec un message clair
git commit -m "feat: ajouter fonctionnalité X"
```

**Conventions de messages de commit** :
- Utiliser des messages clairs et concis
- Préfixer avec le type de changement (`feat:`, `fix:`, `docs:`, etc.)
- Référencer l'issue si applicable (`fixes #123`)
- Max 72 caractères pour la première ligne
- Ajouter une description détaillée si nécessaire

### 6. Pousser et créer une Pull Request

```bash
# Pousser la branche vers le dépôt distant
git push origin feat/nom-de-la-fonctionnalite
```

Puis créer une Pull Request via GitHub :
1. Aller sur la page du dépôt
2. Cliquer sur "Pull Requests"
3. Cliquer sur "New Pull Request"
4. Sélectionner votre branche comme "compare"
5. Remplir le template de PR

### 7. Review et Merge

- **Review** : Au moins un membre de l'équipe doit reviewer
- **CI/CD** : Toutes les vérifications doivent passer
- **Approbation** : Requiert l'approbation du maintainer
- **Merge** : Seul le maintainer peut merger

---

## Conventions de Code

### JavaScript/TypeScript (Next.js)

- **Style Guide** : [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- **TypeScript** : `strict: true` dans tsconfig.json
- **Nommage** : camelCase pour les variables et fonctions, PascalCase pour les composants
- **Components** : Un composant par fichier, dans `components/`
- **Hooks** : Préfixer avec `use` (ex: `useCounter`)
- **Types** : Définir dans des fichiers `.types.ts` ou `.d.ts`

### Python (FastAPI)

- **Style Guide** : [PEP 8](https://peps.python.org/pep-0008/)
- **Type Hints** : Toujours utiliser les type hints
- **Nommage** : snake_case pour les variables et fonctions, PascalCase pour les classes
- **SQLAlchemy** : Utiliser les modèles déclaratifs
- **Pydantic** : Pour la validation des données
- **Imports** : Grouper par standard library, third-party, local

### SQL

- **Nommage** : snake_case pour les tables et colonnes
- **Conventions** : Préfixer les tables avec le module (ex: `auth_users`)
- **Migrations** : Toujours créer des migrations via Alembic
- **Indexes** : Ajouter des indexes pour les colonnes fréquemment queryées

### CSS (Tailwind)

- **Utility-first** : Utiliser les classes utilitaires de Tailwind
- **Components** : Extraire les composants réutilisables dans `@/components`
- **Custom CSS** : Minimiser, utiliser Tailwind autant que possible
- **Responsive** : Toujours penser mobile-first

---

## Structure des Pull Requests

### Titre

- Clair et concis
- Utiliser la convention `type: description`
- Exemple : `feat: ajouter authentification parent`

### Description

Inclure :
1. **Quoi** : Ce que change la PR
2. **Pourquoi** : La raison du changement
3. **Comment** : Brève description de l'implémentation
4. **Tests** : Quels tests ont été ajoutés/modifiés
5. **Documentation** : Quelles docs ont été mises à jour
6. **Screenshots** : Si applicable (UI changes)
7. **Issues liées** : Référencer les issues (ex: `closes #123`)

### Checklist

- [ ] J'ai lu le [PROMPT_GENERAL.md](steps/PROMPT_GENERAL.md)
- [ ] J'ai lu le [DECISIONS_FINALES.md](steps/DECISIONS_FINALES.md)
- [ ] Mon code suit les conventions du projet
- [ ] J'ai ajouté des tests pour les nouvelles fonctionnalités
- [ ] Toutes les tests existantes passent
- [ ] J'ai mis à jour la documentation si nécessaire
- [ ] Mon code ne contient pas de secrets
- [ ] J'ai vérifié avec `npm audit` et `bandit -r apps/api/`
- [ ] Ma PR cible la bonne branche (main ou feature branch)

---

## Definition of Ready (DoR)

Une tâche est prête à être développée si :

- [ ] Objectif et valeur clairement définis
- [ ] Prérequis satisfaits
- [ ] Critères d'acceptation vérifiables
- [ ] Données fictives définies (si applicable)
- [ ] Impact sur le schéma identifié (si applicable)
- [ ] Aucune décision bloquante cachée

---

## Definition of Done (DoD)

Une tâche est terminée si :

- [ ] Critères d'acceptation passés
- [ ] Tests pertinents exécutés et réussis
- [ ] Lint et type-check réussis
- [ ] Sécurité vérifiée selon le périmètre
- [ ] Documentation mise à jour
- [ ] Aucun secret ni donnée réelle
- [ ] Rapport créé (pour les tâches steps/)
- [ ] ETAT.md mis à jour
- [ ] PLANNING.md mis à jour
- [ ] Prochaine étape explicitée

---

## Branching Strategy

### Branches principales

| Branche | Description | Protection |
|---------|-------------|------------|
| `main` | Branche de production (stable) | ✅ Protected |
| `develop` | Branche de développement (à créer) | ⚠️ WIP |

### Feature Branches

- Créées depuis `main` (ou `develop` quand disponible)
- Merge vers `main` via Pull Request
- Nom : `feat/nom-de-la-fonctionnalite`

### Bug Fix Branches

- Créées depuis `main`
- Merge vers `main` via Pull Request
- Nom : `fix/description-du-bug`

### Release Branches

- À créer pour les versions majeures
- Nom : `release/v0.1`
- Merge vers `main` et `develop` après release

### Hotfix Branches

- Créées depuis `main` pour les corrections urgentes
- Merge vers `main` et `develop`
- Nom : `hotfix/description`

---

## Review Guidelines

### Pour les Reviewers

- **Vérifier la compréhension** : Le code fait-il ce qu'il devrait ?
- **Vérifier la qualité** : Le code suit-il les conventions ?
- **Vérifier les tests** : Y a-t-il des tests suffisant ?
- **Vérifier la documentation** : La documentation est-elle à jour ?
- **Vérifier la sécurité** : Y a-t-il des vulnérabilités potentielles ?
- **Être constructif** : Commentaires clairs et actionnables
- **Approuver rapidement** : Ne pas bloquer sans raison valable

### Pour les Auteurs

- **Répondre aux commentaires** : Adresser tous les points soulevés
- **Pousser les corrections** : Mettre à jour la PR avec les changements
- **Ne pas forcer le push** : `git push --force` est interdit
- **Squash si nécessaire** : Le maintainer peut demander un squash

---

## Labels GitHub

| Label | Description |
|-------|-------------|
| `bug` | Bug ou problème
| `enhancement` | Nouvelle fonctionnalité
| `documentation` | Amélioration de la documentation
| `good first issue` | Bonne première contribution
| `help wanted` | Besoin d'aide
| `priority: high` | Priorité élevée
| `priority: low` | Priorité faible
| `status: blocked` | Bloqué par autre chose
| `status: wip` | Travail en cours
| `type: frontend` | Changement frontend
| `type: backend` | Changement backend
| `type: infrastructure` | Changement infrastructure

---

## Communication

### Canaux de communication

- **Issues GitHub** : Pour les discussions techniques
- **Pull Requests** : Pour le review de code
- **Email** : Pour les questions privées ou sensibles

### Bonnes pratiques

- **Être respectueux** : Toujours
- **Rester professionnel** : Même en désaccord
- **Être clair** : Expliquer votre point de vue
- **Être patient** : Les reviews peuvent prendre du temps
- **Demander de l'aide** : Si vous êtes bloqué

---

## Ressources

- [Documentation Officielle](docs/)
- [Architecture](docs/architecture/)
- [ADRs](docs/adr/)
- [API Documentation](docs/api/)
- [User Guide](docs/user-guide/)
- [Planning](steps/PLANNING.md)
- [État du Projet](steps/ETAT.md)

---

## Recognition

Tous les contributeurs sont reconnus dans le fichier [CONTRIBUTORS.md](CONTRIBUTORS.md) (à créer).

---

## Licence

En contribuant, vous acceptez que vos contributions soient sous la même licence que le projet. Voir [LICENSE](LICENSE) pour plus de détails.

---

*Dernière mise à jour : 10 août 2026*
