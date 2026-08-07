# État actuel du projet StudentConnect

## Métadonnées

- Projet : StudentConnect
- Organisation GitHub : `tidianesarrndiaye-org`
- Dépôt : `StudentConnect`
- GitHub Project : `Plateforme familiale élève - Stage Casablanca 2026`
- Contexte : stage présentiel à Casablanca
- Date de référence : 7 août 2026
- Version cible : prototype V0.1
- Stack retenue : Django, DRF, Django Templates, **Bootstrap 5**, HTMX, PostgreSQL, pytest, Docker Compose et GitHub Actions

## Terminé

- [x] Reformulation de la mission et problématique.
- [x] Benchmark initial : OpenEMIS, Moodle, Microsoft Education Insights, Canvas, outils adaptatifs et dossier classique.
- [x] Fiche de cadrage.
- [x] Cahier des charges fonctionnel V1.
- [x] Cahier des charges fonctionnel V2 recentré sur l’élève et les parents.
- [x] Extension du benchmark EdTech, notamment Silicon Valley et open source.
- [x] Analyse des fournisseurs Khan Academy, Khan Academy Kids, CK-12, H5P, PhET, Kolibri, Moodle et Open edX.
- [x] Tests manuels de comptes Khan Academy, H5P et CK-12.
- [x] Test d’un embed CK-12 et constat de redirection vers CK-12.
- [x] Documentation de l’absence d’API publique générale clairement documentée pour Khan Academy et CK-12 dans le périmètre étudié.
- [x] Définition du positionnement différenciant : dossier longitudinal, lacunes localisées, lacunes générales et croisement entre matières.
- [x] Planning détaillé GitHub Project.
- [x] GitHub Project créé avec les vues Backlog, Sprint actuel, Roadmap, Livrables, Bugs et blocages, Validation finale.
- [x] Cahier des charges technique V1 rédigé.
- [x] Décision d’utiliser Bootstrap au lieu de Tailwind CSS.

## En cours

- [ ] Validation finale du périmètre technique V0.1.
- [ ] Complétion des champs, itérations, Epics et issues dans GitHub Project.
- [ ] Choix définitif du programme scolaire, de la classe pilote et des trois matières.
- [ ] Choix du mode précis d’hébergement H5P.
- [ ] Vérification de l’état réel du dépôt et de sa structure initiale.

## À faire en priorité

1. Exécuter `01_gouvernance_et_audit`.
2. Exécuter `02_socle_technique`.
3. Définir le référentiel pilote dans `03_referentiel_et_donnees`.
4. Cataloguer 20 ressources dans `04_catalogue_et_integrations`.
5. Concevoir les maquettes Bootstrap dans `05_ux_et_parcours`.
6. Développer le flux vertical via les étapes 06 à 10.
7. Tester, déployer et documenter via les étapes 11 à 13.

## Décisions validées

- Les utilisateurs centraux sont l’élève et le parent/tuteur.
- L’enseignant ou valideur est facultatif dans la V0.1.
- Les données du prototype sont fictives uniquement.
- L’architecture est un monolithe modulaire Django.
- Bootstrap 5 remplace Tailwind CSS.
- PostgreSQL porte les relations de compétences pour la V0.1.
- H5P est la piste principale pour les évaluations contrôlées.
- CK-12, Khan Academy et PhET sont utilisés par liens, embeds autorisés ou enveloppe interne.
- Kolibri est un spike offline non bloquant.
- Aucune API non officielle ne doit être critique.

## Décisions encore ouvertes

- Programme scolaire et pays de référence.
- Classe ou tranche d’âge pilote.
- Trois matières prioritaires.
- Liste des 10 à 20 compétences pilotes.
- Hébergement H5P : natif, Moodle pilote ou autre moteur compatible.
- Hébergeur de démonstration.
- Niveau exact du spike Kolibri.
- Politique de conservation et suppression des données en phase future.

## Risques actuels

- Périmètre trop large pour la durée du stage.
- Blocage par une intégration externe non documentée.
- Complexité du croisement de compétences entre matières.
- Retard dans la définition du référentiel pilote.
- POC H5P plus complexe que prévu.
- Temps insuffisant pour l’offline et le déploiement.

## Dernier rapport traité

Aucun rapport d’agent dans cette archive au moment de sa création.

## Historique des mises à jour

- 2026-08-07 : création du fichier d’état initial.
