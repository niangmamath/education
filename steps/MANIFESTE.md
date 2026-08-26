# Manifeste

Inventaire des fiches d'étape et des documents de pilotage, avec les douze
premiers caractères de leur empreinte SHA-256. Les rapports de validation
`rapport_*.md` en sont exclus : ils s'ajoutent au fil des clôtures et les
inventorier condamnerait ce fichier à être périmé en permanence. `MANIFESTE.md`
ne peut pas figurer dans sa propre liste.

Régénérer après toute création, suppression ou renommage de fiche :

```
cd steps && find . -type f -name '*.md' ! -name 'MANIFESTE.md' ! -name 'rapport_*.md' -printf '%P\n' | LC_ALL=C sort | while read -r f; do printf -- '- `%s`  `%s`\n' "$f" "$(sha256sum "$f" | cut -c1-12)"; done
```

Nombre de fiches : 99

- `01_gouvernance_et_audit/01_verifier_depot_vide.md`  `0397b9fe23e4`
- `01_gouvernance_et_audit/02_creer_fichiers_racine.md`  `e0bae8ab81a1`
- `01_gouvernance_et_audit/03_creer_adr_initiaux.md`  `6db764a82cb2`
- `01_gouvernance_et_audit/README.md`  `52b40d24642c`
- `02_initialisation_monorepo/01_initialiser_workspace.md`  `e39686bb5142`
- `02_initialisation_monorepo/02_initialiser_nextjs.md`  `6cf2ae1db0e2`
- `02_initialisation_monorepo/03_initialiser_fastapi.md`  `68afd7110f7e`
- `02_initialisation_monorepo/README.md`  `77b87adcf85d`
- `03_infrastructure_locale_ci/01_docker_compose.md`  `46e9cebdc8d5`
- `03_infrastructure_locale_ci/02_configurer_base_migrations.md`  `d118fb6a4861`
- `03_infrastructure_locale_ci/03_configurer_ci.md`  `83e860101a23`
- `03_infrastructure_locale_ci/04_cloturer_etape.md`  `faee6c061fb9`
- `03_infrastructure_locale_ci/README.md`  `3b6ee2c3feef`
- `04_spike_h5p_critique/01_definir_protocole_et_paquets.md`  `4ecae7292dca`
- `04_spike_h5p_critique/02_preparer_lecteur_standalone.md`  `ac97e4a6334c`
- `04_spike_h5p_critique/03_capturer_evenements_xapi.md`  `814ae0e8c2fc`
- `04_spike_h5p_critique/04_analyser_compatibilite_securite.md`  `c971cf4511ca`
- `04_spike_h5p_critique/05_cloturer_spike.md`  `481dade9ef25`
- `04_spike_h5p_critique/README.md`  `5c4773d89f93`
- `05_ux_design_navigation/01_inventorier_parcours_utilisateurs.md`  `aa4b5bec95d0`
- `05_ux_design_navigation/02_definir_routes_navigation.md`  `e24c452baf9f`
- `05_ux_design_navigation/03_definir_design_system_bootstrap.md`  `19f19f71a8dd`
- `05_ux_design_navigation/04_concevoir_layout_parent.md`  `ea3c4b3b4cb4`
- `05_ux_design_navigation/05_concevoir_layout_eleve.md`  `e91e8f5fe49f`
- `05_ux_design_navigation/06_definir_etats_accessibilite.md`  `1bf7de67f7b4`
- `05_ux_design_navigation/07_cloturer_etape.md`  `a25b0381bcda`
- `05_ux_design_navigation/README.md`  `ac172f2e8ce9`
- `06_backend_identite_famille/01_modeles_users.md`  `e3952beeda17`
- `06_backend_identite_famille/02_auth_parent_sessions.md`  `3004bb35c05d`
- `06_backend_identite_famille/03_acces_enfant.md`  `1e7173a1aa0c`
- `06_backend_identite_famille/04_cloturer_etape.md`  `7f6482774bf8`
- `06_backend_identite_famille/README.md`  `4630263ae7c4`
- `07_referentiel_competences/01_modeles_referentiel.md`  `4200c5c84846`
- `07_referentiel_competences/02_import_referentiel.md`  `27a9a16512d1`
- `07_referentiel_competences/03_api_competences.md`  `ec470c622989`
- `07_referentiel_competences/04_cloturer_etape.md`  `17ed6d754580`
- `07_referentiel_competences/README.md`  `eaf89b729724`
- `08_catalogue_contenus_activites/01_modeles_catalogue.md`  `57877354ca9d`
- `08_catalogue_contenus_activites/02_contenus_h5p_autorises.md`  `45db55968382`
- `08_catalogue_contenus_activites/03_api_catalogue.md`  `be87c6f564be`
- `08_catalogue_contenus_activites/04_cloturer_etape.md`  `be7900dbe1a1`
- `08_catalogue_contenus_activites/README.md`  `682ac653038d`
- `09_affectations_parcours/01_modeles_affectations.md`  `92ce56b7e70f`
- `09_affectations_parcours/02_api_affectations_parent.md`  `ecea32608b70`
- `09_affectations_parcours/03_api_activites_eleve.md`  `3cc02249ed6a`
- `09_affectations_parcours/04_cloturer_etape.md`  `79399f3c4586`
- `09_affectations_parcours/README.md`  `272beb67e412`
- `10_tentatives_resultats/00_prerequis_runtime_contenu.md`  `01d2b71a035d`
- `10_tentatives_resultats/01_modeles_tentatives.md`  `fb7998381b4a`
- `10_tentatives_resultats/02_api_tentatives.md`  `729c334f5cff`
- `10_tentatives_resultats/03_calcul_resultats.md`  `1c3bb9e0f6cf`
- `10_tentatives_resultats/04_cloturer_etape.md`  `d45c91d1f4f5`
- `10_tentatives_resultats/README.md`  `b152ab7f9762`
- `11_evenements_xapi_progres/01_ingestion_xapi.md`  `478290acd185`
- `11_evenements_xapi_progres/02_liaison_utilisateur.md`  `b69f0d6f5f1a`
- `11_evenements_xapi_progres/03_agregation_progres.md`  `0e0a6921ae58`
- `11_evenements_xapi_progres/04_cloturer_etape.md`  `3d8264f724e8`
- `11_evenements_xapi_progres/README.md`  `8793cdefb402`
- `12_diagnostic_remediation/01_regles_diagnostic.md`  `1a63e61afd7e`
- `12_diagnostic_remediation/02_moteur_recommandation.md`  `159f268bf360`
- `12_diagnostic_remediation/03_api_diagnostic.md`  `b86e5b117d2f`
- `12_diagnostic_remediation/04_cloturer_etape.md`  `a1ef826916c6`
- `12_diagnostic_remediation/README.md`  `fa479472c7c5`
- `13_dashboards/01_dashboard_eleve.md`  `3186f8486784`
- `13_dashboards/02_dashboard_parent.md`  `df3083e4946e`
- `13_dashboards/03_notifications.md`  `c19b5ac558cb`
- `13_dashboards/04_cloturer_etape.md`  `5b4f511d9b66`
- `13_dashboards/README.md`  `9a98c4c9d054`
- `14_evaluation_par_paliers/01_moteur_de_paliers.md`  `fdd630063d29`
- `14_evaluation_par_paliers/02_examen_par_palier.md`  `14e6d5994fa1`
- `14_evaluation_par_paliers/03_diagnostic_generalise.md`  `da415fcf9488`
- `14_evaluation_par_paliers/04_boucle_de_bout_en_bout.md`  `51667738ea50`
- `14_evaluation_par_paliers/05_documentation_dette_cloture.md`  `9d6f9172af87`
- `14_evaluation_par_paliers/README.md`  `90f437e8b60e`
- `15_cours_escalade_competences/README.md`  `566be6db67db`
- `16_notifications/01_modeles_preferences.md`  `4ec2b5da22a7`
- `16_notifications/02_evenements_notifications.md`  `d6e33777a3c9`
- `16_notifications/03_api_notifications.md`  `608ae2599aef`
- `16_notifications/04_cloturer_etape.md`  `7d996f109509`
- `16_notifications/README.md`  `10f282f6b00f`
- `17_administration_securite_exploitation/01_administration.md`  `13ba2a1593f2`
- `17_administration_securite_exploitation/02_securite_applicative.md`  `5e9f240ab9e5`
- `17_administration_securite_exploitation/03_observabilite_sauvegarde.md`  `45c853e3a46b`
- `17_administration_securite_exploitation/04_cloturer_etape.md`  `c8984b4561d0`
- `17_administration_securite_exploitation/README.md`  `b886dff6150b`
- `18_validation_mvp_livraison/01_tests_end_to_end.md`  `dab1c140a062`
- `18_validation_mvp_livraison/02_donnees_demo.md`  `d1e59d1bf13e`
- `18_validation_mvp_livraison/03_deploiement_demo.md`  `96c12283f5c9`
- `18_validation_mvp_livraison/04_documentation_livraison.md`  `ec9ba5047212`
- `18_validation_mvp_livraison/05_cloturer_mvp.md`  `6b925de8f7a1`
- `18_validation_mvp_livraison/README.md`  `87bcc20f4dd2`
- `AGENTS.md`  `d3620f0f65bb`
- `DECISIONS_FINALES.md`  `46e9dcd69815`
- `ETAT.md`  `f86d73150580`
- `MODELE_RAPPORT.md`  `d391f4da239a`
- `PLANNING.md`  `399293d3c88b`
- `PROMPT_GENERAL.md`  `d9ff17c723a2`
- `RAPPORTS_REGLES.md`  `9c07f684b281`
- `README.md`  `afd8cf95e4b3`
