# Étape 05, UX design et navigation

## Objectif

Définir et valider l’architecture UX du MVP StudentConnect avant d’implémenter les fonctionnalités métier. L’étape prépare un design system Bootstrap, les routes, les layouts Parent et Élève, ainsi que les états d’interface et les règles d’accessibilité.

## Périmètre

1. Inventaire des utilisateurs et de leurs parcours.
2. Cartographie des routes publiques et protégées.
3. Design system Bootstrap propre à StudentConnect.
4. Layout et navigation de l’espace Parent.
5. Layout et navigation de l’espace Élève.
6. États chargement, vide, erreur, succès et accès refusé.
7. Vérification responsive et accessibilité de base.

## Hors périmètre

- authentification complète ;
- modèles métier et persistance ;
- score académique réel ;
- moteur de recommandation ;
- stockage xAPI backend ;
- import H5P de production ;
- notifications réelles.

## Règles

- Branche obligatoire : `feat/ux-design-navigation`.
- Bootstrap est la cible visuelle de StudentConnect.
- Les données de démonstration doivent être explicitement identifiées comme fictives.
- Aucun rapport ne peut être marqué terminé avant les contrôles réels.
- Les choix doivent fonctionner sur mobile et au clavier.
- Les interfaces Parent et Élève doivent rester distinctes.

## Ordre d’exécution

1. `01_inventorier_parcours_utilisateurs.md`
2. `02_definir_routes_navigation.md`
3. `03_definir_design_system_bootstrap.md`
4. `04_concevoir_layout_parent.md`
5. `05_concevoir_layout_eleve.md`
6. `06_definir_etats_accessibilite.md`
7. `07_cloturer_etape.md`

## Critère de réussite

L’étape est réussie lorsque les parcours, routes, composants et layouts sont documentés, implémentés sous forme de socle visuel reproductible, contrôlés sur plusieurs tailles d’écran et validés par TypeScript, ESLint et le build Next.js.
