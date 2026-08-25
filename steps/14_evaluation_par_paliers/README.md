# Étape 14, évaluation par paliers

## Objectif

Remplacer l'examen d'entrée statique, qui teste toutes les compétences d'une
classe d'un coup, par une évaluation hiérarchique et séquentielle : un enfant
n'est testé que sur les premières compétences nécessaires de sa classe,
débloque le palier suivant une fois le précédent maîtrisé, et une lacune
déclenche une remédiation ciblant le vrai prérequis en cause — au besoin dans
une classe antérieure — suivie d'un retest qui confirme l'acquisition avant
de rouvrir le palier.

Décision confirmée par le propriétaire le 25 août 2026 : un palier reste
borné à la classe déclarée de l'enfant ; la descente vers une classe
antérieure jamais testée reste réactive, déclenchée par un échec, jamais un
balayage systématique du bas du graphe pour un enfant plus âgé.

Aucune migration n'est nécessaire : comme le diagnostic depuis l'étape 12,
tout se recalcule à la lecture plutôt que d'être stocké.

## Sous-étapes

1. `01_moteur_de_paliers.md` : Moteur de paliers
2. `02_examen_par_palier.md` : Examen servi par palier
3. `03_diagnostic_generalise.md` : Diagnostic généralisé
4. `04_boucle_de_bout_en_bout.md` : Boucle de bout en bout
5. `05_documentation_dette_cloture.md` : Documentation et clôture

## Conditions de clôture

- migrations upgrade et downgrade validées si applicables ;
- Ruff, Mypy et Pytest verts ;
- TypeScript, ESLint et build Next.js verts si le web est modifié ;
- contrôles d'autorisation et d'isolation validés ;
- documentation et preuves produites ;
- commit et push ;
- CI distante applicable réussie ;
- fusion contrôlée vers `main` ;
- ETAT et PLANNING mis à jour après preuves.
