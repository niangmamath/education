# Steps, guide d’exécution de StudentConnect

Cette archive contient un parcours de réalisation de bout en bout, organisé par grandes étapes. Chaque dossier contient des prompts Markdown destinés à un agent de développement.

## Ordre obligatoire

1. Lire `PROMPT_GENERAL.md`.
2. Lire `etat.md`.
3. Ouvrir le dossier de l’étape courante.
4. Exécuter les prompts dans l’ordre numérique.
5. Produire un rapport Markdown après chaque sous-étape.
6. Mettre à jour `etat.md` sans supprimer l’historique.
7. Ne passer à l’étape suivante que si le rapport indique `Terminé`, ou si un report explicite est documenté.

## Étapes

- `01_gouvernance_et_audit`
- `02_socle_technique`
- `03_referentiel_et_donnees`
- `04_catalogue_et_integrations`
- `05_ux_et_parcours`
- `06_comptes_et_dossier`
- `07_evaluations_et_preuves`
- `08_lacunes_et_croisement`
- `09_remediation_et_espace_parent`
- `10_tableaux_de_bord_et_audit`
- `11_tests_et_validation`
- `12_deploiement_et_offline`
- `13_documentation_et_livraison`

## Convention de rapport

Créer un fichier :

`rapport_YYYY-MM-DD_HHMM_<slug>.md`

Le fichier doit rester dans le dossier de l’étape concernée.

## Important

- Bootstrap 5 est obligatoire pour l’interface V0.1.
- Toutes les données sont fictives.
- Ne jamais lancer plusieurs migrations contradictoires dans des branches concurrentes.
- Ne jamais inventer une API fournisseur.
- Ne jamais présenter une activité externe ouverte comme une compétence validée.
