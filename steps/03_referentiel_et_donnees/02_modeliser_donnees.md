# Prompt 03.2, produire MCD, MLD et dictionnaire

Modélise les entités nécessaires au flux vertical, pas toute la vision future.

## Entités minimales

User, GuardianProfile, StudentProfile, FamilyRelation, StudentRecord, Framework, Subject, Competency, CompetencyRelation, ExternalResource, Assessment, Question, Attempt, CompetencyResult, Evidence, LocalizedGap, GeneralGap, RemediationPlan, Reassessment et AuditLog.

## Contraintes

- historique non écrasé ;
- relation de compétence typée ;
- prévention des boucles directes de prérequis ;
- GeneralGap regroupe sans supprimer ;
- source, auteur et date sur les données critiques.

## Livrables

- `docs/architecture/mcd.md`
- `docs/architecture/mld.md`
- `docs/architecture/dictionnaire-donnees.md`
- rapport de réalisation
