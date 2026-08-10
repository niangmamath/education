# ADR-010 : Planning Markdown sans GitHub Project

## Statut

✅ **Accepted** - Décision validée et implémentée

---

## Contexte

StudentConnect doit être **piloté** de manière efficace avec un suivi clair des tâches, dépendances et statut. Plusieurs options existent pour le suivi de projet.

### Problème à résoudre

Choisir une méthode de **pilotage et suivi de projet** qui :
1. Permet un **suivi clair** des tâches
2. Est **simple à maintenir**
3. **S'intègre bien** avec GitHub
4. **Documenté** et versionnable
5. **Collaboratif** pour l'équipe
6. **Adapté** à la taille du projet (MVP)

### Contraintes

- **Pas de GitHub Project** (décision dans DECISIONS_FINALES.md)
- Besoin de **suivre les dépendances** entre tâches
- **Rapports Markdown** par sous-étape
- **ETAT.md** comme source de vérité opérationnelle

---

## Décision

**Utiliser un planning Markdown simple** dans `PLANNING.md` combiné avec `ETAT.md` pour le suivi global.

### Architecture de pilotage

```
Pilotage StudentConnect:
├── steps/ETAT.md              # Source de vérité opérationnelle
│   ├── État des tâches (✅/🔄/❌)
│   ├── Prochaine action
│   └── Décisions ouvertes
│
├── steps/PLANNING.md          # Planning détaillé
│   ├── Phases (00-16)
│   ├── Tâches par phase
│   ├── Statuts (À faire/En cours/En revue/Terminé)
│   └── Dépendances
│
├── steps/MODELE_RAPPORT.md    # Template pour les rapports
│
└── steps/01_gouvernance_et_audit/
    ├── 01_verifier_depot_vide.md
    ├── 02_creer_fichiers_racine.md
    ├── 03_creer_adr_initiaux.md
    └── rapports/
        ├── rapport_YYYY-MM-DD_HHMM_verifier-depot-vide.md
        └── rapport_YYYY-MM-DD_HHMM_creer-fichiers-racine.md
```

---

## Options considérées

### 1. Planning Markdown + ETAT.md (Sélectionné)

**Pour** :
- ✅ **Versionnable** : L'historique est dans Git
- ✅ **Lisible** : Format texte simple, accessible à tous
- ✅ **Indépendant** : Pas de dépendance à un outil externe
- ✅ **Flexible** : Peut être adapté à nos besoins
- ✅ **Documentable** : Les décisions sont documentées
- ✅ **Collaboratif** : Les PR permettent le review
- ✅ **Simple** : Pas de configuration complexe
- ✅ **Durable** : Ne dépend pas d'un service tiers

**Contre** :
- ❌ Moins visuel qu'un tableau Kanban
- ❌ Pas de drag-and-drop
- ❌ Moins adapté aux très grandes équipes

**Verdict** : ✅ **Sélectionné** - Parfait pour notre taille et besoins

---

### 2. GitHub Project (Rejeté explicitement)

**Pour** :
- ✅ Tableau Kanban visuel
- ✅ Drag-and-drop
- ✅ Intégration native avec GitHub
- ✅ Automation possible

**Contre** :
- ❌ **Explicitement interdit** par DECISIONS_FINALES.md
- ❌ Pas versionnable
- ❌ Dépendance à GitHub
- ❌ Complexité pour un MVP

**Verdict** : ❌ **Rejeté** - Explicitement interdit

---

### 3. Trello / Jira / Notion

**Pour** :
- ✅ Outils matures
- ✅ Très visuels
- ✅ Nombreuses features

**Contre** :
- ❌ **Dépendance externe** (SaaS)
- ❌ Pas versionnable
- ❌ Coût potentiel
- ❌ Moins intégré avec GitHub
- ❌ Risque de lock-in

**Verdict** : ❌ **Rejeté** - Dépendance externe et coût

---

### 4. GitHub Issues + Milestones

**Pour** :
- ✅ Natif GitHub
- ✅ Versionnable via Git
- ✅ Intégration avec PRs

**Contre** :
- ❌ Moins structuré pour un planning global
- ❌ Difficile de voir les dépendances
- ❌ Pas adapté pour un MVP avec beaucoup de tâches

**Verdict** : ❌ **Rejeté** - Pas assez structuré

---

### 5. ZenHub / Linear

**Pour** :
- ✅ Outils modernes
- ✅ Intégration GitHub
- ✅ Visuel

**Contre** :
- ❌ Dépendance externe
- ❌ Coût
- ❌ Complexité

**Verdict** : ❌ **Rejeté** - Dépendance et coût

---

## Conséquences

### Avantages

- **Transparence totale** : Tout le monde voit l'état du projet
- **Historique complet** : Toutes les décisions et changements sont dans Git
- **Indépendance** : Pas de dépendance à un service tiers
- **Simplicité** : Pas de configuration complexe
- **Collaboration** : Les PR permettent le review des changements
- **Documentation** : Les décisions sont documentées avec les tâches
- **Flexibilité** : Peut être adapté selon les besoins

### Inconvénients

- **Moins visuel** : Pas de tableau Kanban interactif
- **Moins adapté aux grandes équipes** : Devient difficile à gérer avec 50+ personnes
- **Maintenance manuelle** : Nécessite de garder les fichiers à jour

### Mitigations

- **Scripts** : Scripts pour automatiser certaines mises à jour
- **Templates** : Templates pour créer facilement de nouvelles tâches
- **Review systématique** : Review des changements de planning via PR
- **Sync périodique** : Synchronisation avec les issues GitHub si nécessaire

---

## Implémentation

### Structure de PLANNING.md

```markdown
# Planning simple de développement

## Principes

- Le planning est la source de pilotage principale
- Chaque ligne passe par : À faire, En cours, Bloqué, En revue, Terminé
- Une tâche bloquée doit référencer un rapport
- Les dates sont ajustables, mais les dépendances ne doivent pas être ignorées

## Phase 0, préparation et spike critique

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| P0-01 | Vérifier le dépôt vidé | Aucune | Terminé | Rapport d'audit |
| P0-02 | Recréer les fichiers racine | P0-01 | Terminé | README, gitignore, env example |
| P0-03 | Initialiser le monorepo | P0-02 | À faire | Apps et packages |

## Sprint 1, fondations et identité familiale

| ID | Travail | Dépendance | Statut | Livrable |
|---|---|---|---|---|
| S1-01 | Initialiser Next.js et Tailwind | P0-03 | À faire | Frontend |
| S1-02 | Initialiser FastAPI | P0-03 | À faire | Backend |
...
```

### Structure de ETAT.md

```markdown
# État initial du projet

## Métadonnées
- Projet : StudentConnect
- Date de référence : 10 août 2026
- Version cible : V0.1

## Terminé avant reconstruction
- [x] Cahier des charges fonctionnel initial
- [x] Décisions finales de stack

## État du code
- [x] Dépôt vidé
- [x] README recréé
- [x] .gitignore recréé
- [ ] Monorepo initialisé
- [ ] Infrastructure locale opérationnelle

## Prochaine action
Exécuter : steps/01_gouvernance_et_audit/03_creer_adr_initiaux.md

## Décisions ouvertes à contrôler
- Hébergeur Next.js
- Hébergeur FastAPI
- Licence du projet
```

### Workflow de mise à jour

1. **Avant de commencer une tâche** :
   - Vérifier que tous les prérequis sont marqués comme terminés dans PLANNING.md
   - Vérifier qu'il n'y a pas de blocage dans ETAT.md
   - S'assigner la tâche (commentaire GitHub ou mise à jour locale)

2. **Pendant la tâche** :
   - Mettre à jour le statut dans PLANNING.md à "En cours"
   - Créer un rapport selon MODELE_RAPPORT.md

3. **À la fin de la tâche** :
   - Vérifier tous les critères d'acceptation
   - Mettre à jour le statut dans PLANNING.md à "Terminé" ou "En revue"
   - Mettre à jour ETAT.md
   - Commiter les changements avec une PR

4. **Si bloqué** :
   - Mettre à jour le statut à "Bloqué"
   - Documenter le blocage dans le rapport
   - Référencer le rapport dans PLANNING.md

---

## Risques

| Risque | Probabilité | Impact | Mitigation |
|-------|-------------|--------|------------|
| Planning obsolète | Moyenne | Moyen | Review régulier, PR pour les changements |
| Tâches oubliées | Moyenne | Moyen | Vérification systématique, checklist |
| Dépendances ignorées | Faible | Élevé | Validation automatique, review PR |
| Manque de visibilité | Faible | Moyen | Standup réguliers, revues de planning |

---

## Références

- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Markdown Tables](https://github.github.com/gfm/#tables-extension-)
- [Task Lists](https://github.blog/2013-01-09-task-lists-in-gfm-issues-pulls-comments/)

---

## Historique

| Date | Auteur | Action |
|------|--------|--------|
| 2026-08-10 | Mistral Vibe | Création initiale (Accepted) |

---

## Annexes

### Comparaison des outils de planning

| Critère | Planning MD | GitHub Project | Trello | Jira |
|---------|-------------|----------------|--------|------|
| Versionnable | ✅ Oui | ❌ Non | ❌ Non | ❌ Non |
| Visuel | ⚠️ Tableau MD | ✅ Kanban | ✅ Kanban | ✅ Kanban |
| Dépendances | ✅ Claires | ✅ Bon | ❌ Limité | ✅ Bon |
| Collaboratif | ✅ PR | ✅ Natif | ✅ Natif | ✅ Natif |
| Intégration GitHub | ✅ Forte | ✅ Natif | ⚠️ API | ⚠️ API |
| Coût | ✅ Gratuit | ✅ Gratuit | ❌ Payant | ❌ Payant |
| Complexité | ✅ Faible | ⚠️ Moyenne | ✅ Faible | ❌ Élevée |
| Évolutivité | ⚠️ Moyenne | ✅ Bonne | ⚠️ Moyenne | ✅ Bonne |

### Bonnes pratiques

1. **Garder les fichiers à jour** : Toujours mettre à jour PLANNING.md et ETAT.md
2. **Utiliser des PR** : Pour les changements de planning significatifs
3. **Review les dépendances** : Vérifier que les dépendances sont respectées
4. **Documenter les blocages** : Toujours documenter pourquoi une tâche est bloquée
5. **Valider les critères** : Ne pas marquer comme terminé si les critères ne sont pas remplis
6. **Faire des reviews** : Review régulier du planning avec l'équipe
7. **Prioriser** : Marquer clairement les tâches prioritaires
8. **Estimer** : Ajouter des estimations de temps si utile
