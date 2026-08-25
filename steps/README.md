# StudentConnect, parcours complet de réalisation

Ce dossier `steps` permet de reconstruire **StudentConnect depuis un dépôt entièrement vide**, y compris sans `.gitignore`, sans `README`, sans configuration et sans code.

## Ordre de travail obligatoire

1. Lire `PROMPT_GENERAL.md`.
2. Lire `DECISIONS_FINALES.md`.
3. Lire `ETAT.md`.
4. Lire `PLANNING.md`.
5. Exécuter les dossiers d’étapes dans l’ordre numérique.
6. À l’intérieur d’une étape, exécuter les prompts dans l’ordre numérique.
7. Après chaque prompt, créer un rapport dans le dossier de l’étape.
8. Mettre à jour `ETAT.md` après chaque sous-étape terminée ou bloquée.
9. Ne jamais commencer une nouvelle étape si les prérequis ne sont pas satisfaits.

## Convention de rapport

Nom obligatoire :

```text
rapport_YYYY-MM-DD_HHMM_<slug>.md
```

Exemple :

```text
steps/02_initialisation_monorepo/rapport_2026-08-11_1530_initialisation.md
```

## Étapes

1. Gouvernance et audit du dépôt vide
2. Initialisation du monorepo
3. Infrastructure locale et CI
4. Spike H5P critique
5. UX, design system et navigation
6. Backend, identité et famille
7. Référentiel de compétences
8. Catalogue de contenus et activités
9. Affectations et parcours
10. Tentatives et résultats
11. Événements xAPI et progrès
12. Diagnostic et remédiation
13. Dashboards Élève et Parent
14. Évaluation par paliers
15. Cours d’escalade de compétences (brouillon)
16. Notifications
17. Administration, sécurité et exploitation
18. Validation, MVP et livraison

## Important

- Le dépôt est considéré comme vide au départ.
- Le projet ne dépend pas de GitHub Project.
- Le planning est maintenu dans `PLANNING.md`.
- Ne pas utiliser Django, Moodle ou CK-12 dans l’architecture active. Bootstrap
  5.3.8 est le design system retenu depuis l’étape 05 (ADR-002 amendée),
  Tailwind ayant été retiré.
- Ne pas réintroduire les anciennes décisions sans ADR validé.
