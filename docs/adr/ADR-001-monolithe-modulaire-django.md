# ADR-001 : Monolithe modulaire Django

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

StudentConnect V0.1 est un prototype démontrable à livrer en un mois de stage (5 août – 4 septembre 2026). Le périmètre couvre onze domaines fonctionnels (M01–M11) mais le flux vertical MVP doit rester limité. L’équipe est réduite et le déploiement cible une démonstration unique, pas une montée en charge distribuée.

## Décision

Adopter une **architecture monolithe modulaire Django** : une seule application déployable, organisée en apps Django par domaine (`accounts`, `students`, `competencies`, etc.), sans microservices ni services séparés pour la V0.1.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **Monolithe modulaire Django** (retenue) | Rapidité de développement, ORM unifié, écosystème mature, déploiement simple | Couplage plus fort, scaling vertical limité |
| Microservices | Isolation par domaine, scaling indépendant | Surcoût opérationnel, complexité réseau, hors délai stage |
| Django + SPA séparée (React/Vue) | UX riche | Double codebase, délai front-end, hors stack retenue |
| Headless CMS + couche custom | Contenu éditorial flexible | Dépendance externe, incohérent avec dossier longitudinal |

## Conséquences

- Une base de code, un processus de déploiement, une migration schema unique.
- Les modules M01–M11 sont des **apps Django**, pas des services autonomes.
- DRF expose une API interne ou partielle ; l’UI principale reste Django Templates + Bootstrap + HTMX.
- Toute extraction future en service nécessitera un ADR ultérieur.

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Monolithe difficile à tester par module | P2 | Apps isolées, tests pytest par app |
| Tentation de sur-développer tous les modules | P1 | Flux vertical V0.1 strict dans le GitHub Project |
| Dette si front SPA ajouté plus tard | P3 | ADR requis avant changement de paradigme UI |

## Références

- `steps/PROMPT_GENERAL.md` §4, §5, §8
- `steps/etat.md` — Décisions validées
