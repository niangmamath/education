# Étape 04, spike H5P critique

## Finalité

Démontrer, avec des preuves reproductibles, qu’un paquet H5P autorisé peut être lu dans StudentConnect sans serveur H5P complet et qu’un événement xAPI exploitable peut être capturé.

## Périmètre

Cette étape est un spike technique. Elle ne doit pas implémenter le Content Studio, le stockage métier, la publication, la remédiation ou les dashboards.

## Ordre d’exécution

1. `01_definir_protocole_et_paquets.md`
2. `02_preparer_lecteur_standalone.md`
3. `03_capturer_evenements_xapi.md`
4. `04_analyser_compatibilite_securite.md`
5. `05_cloturer_spike.md`

## Règles

- Travailler dans une branche `spike/h5p-critical`.
- Conserver les paquets `.h5p` hors de Git tant que leur licence et leur provenance ne sont pas validées.
- Enregistrer l’URL d’origine, la licence, le type, la version et le SHA-256 de chaque paquet.
- Ne jamais annoncer le spike comme réussi sans rendu visuel et événement xAPI réels.
- Ne pas mettre à jour `ETAT.md` ou `PLANNING.md` vers Terminé avant le rapport final.

## Critère de succès minimal

- un paquet H5P extrait et rendu localement ;
- au moins un événement xAPI capturé avec `event.data.statement` ;
- provenance et licence documentées ;
- limites et risques documentés ;
- décision explicite : poursuivre, poursuivre sous conditions, ou abandonner.
