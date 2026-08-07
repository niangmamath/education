# Checklist GitHub — actions manuelles

**Date :** 2026-08-07  
**Contexte :** l'agent ne dispose pas du scope `read:project` ; la configuration GitHub Project n'a pas pu être auditée automatiquement.

---

## Authentification CLI

```powershell
gh auth refresh -s read:project,project
```

---

## GitHub Project « Plateforme familiale élève - Stage Casablanca 2026 »

### Vues à vérifier

- [x] Backlog
- [x] Sprint actuel
- [x] Roadmap
- [x] Livrables
- [x] Bugs et blocages
- [x] Validation finale

### Champs à vérifier

- [x] Status
- [x] Priority
- [x] Iteration
- [x] Epic / Module
- [x] Type
- [x] MoSCoW
- [x] Estimate
- [x] Start date
- [x] Target date
- [x] Deliverable
- [x] Risk
- [x] Acceptance



### Itérations

- [x] I0 — cadrage consolidé (5–11 août 2026)
- [x] I1 — conception prête (12–18 août)
- [x] I2 — prototype vertical (19–25 août)
- [x] I3 — validation finale (26 août – 4 sept.)

---



## Labels recommandés



### Modules (M01–M11)

```
M01-accounts, M02-students, M03-competencies, M04-resources,
M05-learning, M06-assessments, M07-gaps, M08-remediation,
M09-parent, M10-dashboards, M11-admin
```



### Priorité

```
P0-critical, P1-high, P2-medium, P3-low
```



### Type

```
type-feature, type-bug, type-decision, type-test, type-docs, type-spike
```

Commande exemple :

```powershell
gh label create "M03-competencies" --description "Epic référentiel compétences" --color "1D76DB"
gh label create "P0-critical" --description "Bloquant" --color "B60205"
```

---



## Issues recommandées à créer

- [ ] `[decision] Hébergement H5P` — P1, Epic M04/M06
- [ ] `[decision] Référentiel pilote (programme, matières, compétences)` — P1, Epic M03
- [ ] `[M11] Initialiser socle Django` — P0, Itération I0/I1

---



## Protection de branche `main`

Si autorisé sur le dépôt organisation :

- [ ] Exiger une PR avant merge
- [ ] Exiger statut CI vert (après étape 02.3)
- [ ] Interdire force push

```powershell
gh api repos/Tidianesarrndiaye-org/StudentConnect/branches/main/protection -X PUT -f required_pull_request_reviews[required_approving_review_count]=1
```

*(Adapter selon politique organisation.)*

---



## Templates dépôt (créés par l'agent)

- [x] `.github/ISSUE_TEMPLATE/feature.md`
- [x] `.github/ISSUE_TEMPLATE/bug.md`
- [x] `.github/ISSUE_TEMPLATE/decision.md`
- [x] `.github/ISSUE_TEMPLATE/test.md`
- [x] `.github/pull_request_template.md`
- [x] `CONTRIBUTING.md`

---



## Description du dépôt

Mettre à jour la description GitHub :

```powershell
gh repo edit Tidianesarrndiaye-org/StudentConnect --description "Plateforme familiale élève — prototype V0.1 stage Casablanca 2026"
```

