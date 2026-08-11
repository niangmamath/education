# Contenu et securite du correctif

## Principe de nettoyage

Le script ne supprime ni `.git`, ni `apps/web`, ni le code FastAPI de l'etape 02, ni les packages, ni les ADR, ni les rapports 01/02.

Le script supprime uniquement:

- les prompts des etapes futures 04 a 16;
- l'ancien dossier `steps/03_infrastructure_locale_ci` et ses rapports non fiables;
- les artefacts generes Python/TypeScript;
- les fichiers d'infrastructure 03 explicitement remplaces.

Une sauvegarde horodatee des fichiers remplaces est creee avant suppression.

## Attention

Le correctif ne supprime aucun volume Docker automatiquement. Le reset des volumes exige la saisie manuelle `RESET-LOCAL`.
