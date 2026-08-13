# 05.3, définir le design system Bootstrap

## Objectif

Créer un socle visuel StudentConnect basé sur Bootstrap et planifier la sortie contrôlée de Tailwind CSS actuellement présent.

## Travail

1. Auditer les dépendances et classes Tailwind existantes.
2. Choisir et verrouiller une version Bootstrap compatible.
3. Définir les tokens StudentConnect : couleurs, typographie, rayons, ombres et espacements.
4. Définir les composants : boutons, formulaires, cartes, badges, alertes, navigation, progression et skeletons.
5. Documenter une stratégie de migration sans mélanger durablement Bootstrap et Tailwind.

## Livrables

- `docs/ux/design-system-bootstrap.md` ;
- `docs/ux/migration-tailwind-bootstrap.md` ;
- composants de présentation réutilisables ;
- page de démonstration locale si pertinente.

## Contraintes

- Aucun style critique ne dépend uniquement de la couleur.
- Focus clavier visible.
- Contraste lisible.
- Cibles tactiles adaptées.
- Les composants destinés aux élèves restent simples sans infantilisation excessive.

## Acceptation

- [ ] Bootstrap verrouillé dans le lockfile.
- [ ] Tokens documentés.
- [ ] Composants de base démontrés.
- [ ] Migration Tailwind documentée.
- [ ] Aucun mélange non expliqué des deux systèmes.
