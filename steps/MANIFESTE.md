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

Nombre de fiches : 91

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
- `07_referentiel_competences/02_import_referentiel.md`  `c2c47ab2d4fe`
- `07_referentiel_competences/03_api_competences.md`  `d3112e8ceafd`
- `07_referentiel_competences/04_cloturer_etape.md`  `47bb43c6cf34`
- `07_referentiel_competences/README.md`  `eaf89b729724`
- `08_catalogue_contenus_activites/01_modeles_catalogue.md`  `9ac4a058c7d6`
- `08_catalogue_contenus_activites/02_contenus_h5p_autorises.md`  `e717012a6fad`
- `08_catalogue_contenus_activites/03_api_catalogue.md`  `a8fd2dbd4e80`
- `08_catalogue_contenus_activites/04_cloturer_etape.md`  `b1b05804373a`
- `08_catalogue_contenus_activites/README.md`  `682ac653038d`
- `09_affectations_parcours/01_modeles_affectations.md`  `5790700c737c`
- `09_affectations_parcours/02_api_affectations_parent.md`  `bd76257c166f`
- `09_affectations_parcours/03_api_activites_eleve.md`  `09013872c6b9`
- `09_affectations_parcours/04_cloturer_etape.md`  `7bfc9c6862b8`
- `09_affectations_parcours/README.md`  `272beb67e412`
- `10_tentatives_resultats/01_modeles_tentatives.md`  `71c17eaee060`
- `10_tentatives_resultats/02_api_tentatives.md`  `8a76a35fa1e4`
- `10_tentatives_resultats/03_calcul_resultats.md`  `a698f3bf31f6`
- `10_tentatives_resultats/04_cloturer_etape.md`  `16c9e9934971`
- `10_tentatives_resultats/README.md`  `b152ab7f9762`
- `11_evenements_xapi_progres/01_ingestion_xapi.md`  `6e0b9b2d9d42`
- `11_evenements_xapi_progres/02_liaison_utilisateur.md`  `e04a56a57d16`
- `11_evenements_xapi_progres/03_agregation_progres.md`  `46f07db45504`
- `11_evenements_xapi_progres/04_cloturer_etape.md`  `a1f27cba363f`
- `11_evenements_xapi_progres/README.md`  `8793cdefb402`
- `12_diagnostic_remediation/01_regles_diagnostic.md`  `d76efc249433`
- `12_diagnostic_remediation/02_moteur_recommandation.md`  `6bbd3ca88ea3`
- `12_diagnostic_remediation/03_api_diagnostic.md`  `7e77359b9887`
- `12_diagnostic_remediation/04_cloturer_etape.md`  `fb0b434497ea`
- `12_diagnostic_remediation/README.md`  `fa479472c7c5`
- `13_dashboards/01_dashboard_eleve.md`  `07b3146f1f7d`
- `13_dashboards/02_dashboard_parent.md`  `ed48f19dd7fe`
- `13_dashboards/03_notifications.md`  `b88a345c914e`
- `13_dashboards/04_cloturer_etape.md`  `567c5db399a9`
- `13_dashboards/README.md`  `9a98c4c9d054`
- `14_notifications/01_modeles_preferences.md`  `3f06bb98d0f7`
- `14_notifications/02_evenements_notifications.md`  `0c87b184d605`
- `14_notifications/03_api_notifications.md`  `b120b11c430b`
- `14_notifications/04_cloturer_etape.md`  `47b9281d31e3`
- `14_notifications/README.md`  `4a6e19701edd`
- `15_administration_securite_exploitation/01_administration.md`  `374aeb2bc15b`
- `15_administration_securite_exploitation/02_securite_applicative.md`  `c6cc31e164f3`
- `15_administration_securite_exploitation/03_observabilite_sauvegarde.md`  `7932b817f2d1`
- `15_administration_securite_exploitation/04_cloturer_etape.md`  `ab7428be5f83`
- `15_administration_securite_exploitation/README.md`  `a38311a887d0`
- `16_validation_mvp_livraison/01_tests_end_to_end.md`  `88ca633396ee`
- `16_validation_mvp_livraison/02_donnees_demo.md`  `3d1956950f6a`
- `16_validation_mvp_livraison/03_deploiement_demo.md`  `8780bead9d63`
- `16_validation_mvp_livraison/04_documentation_livraison.md`  `5e1273146d4b`
- `16_validation_mvp_livraison/05_cloturer_mvp.md`  `f991983326fc`
- `16_validation_mvp_livraison/README.md`  `998e5bc3959d`
- `AGENTS.md`  `d3620f0f65bb`
- `DECISIONS_FINALES.md`  `a735c5ca2723`
- `ETAT.md`  `17dc15faf1c7`
- `MODELE_RAPPORT.md`  `d391f4da239a`
- `PLANNING.md`  `4a0119725589`
- `PROMPT_GENERAL.md`  `d9ff17c723a2`
- `RAPPORTS_REGLES.md`  `9c07f684b281`
- `README.md`  `b4684411894a`
