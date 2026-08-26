# Étape 15, cours d'escalade de compétences

## Objectif

Construire la brique qui **enseigne** : un enfant ayant maîtrisé les
compétences d'un palier reçoit, en même temps que l'examen du palier
suivant, un cours natif portant sur ce que ce palier demande — pour qu'elle
puisse apprendre sur la plateforme plutôt que de supposer qu'elle l'a appris
ailleurs, hypothèse sur laquelle reposaient jusqu'ici l'examen et les fiches
de remédiation.

Deux décisions confirmées par le propriétaire le 26 août 2026, avant toute
construction (même démarche qu'à l'ouverture des étapes 07, 08 et 14) :

1. **Don automatique, non bloquant.** Comme l'examen, le cours est donné par
   la plateforme dès qu'un palier est prêt — extension d'un cran de
   l'exception déjà en vigueur (ADR-014, étendue par ADR-021). Ce n'est pas
   une porte : l'examen du palier reste accessible sans être passé par le
   cours.
2. **Leçon native avec vérification à la volée, sans conséquence sur la
   maîtrise.** Une leçon écrite ici, comme les fiches de remédiation
   (ADR-017), suivie de quelques questions expliquées qui gardent l'enfant
   engagée mais ne produisent **aucune** lecture de compétence. La maîtrise
   reste décidée uniquement par l'examen du palier, inchangé.

Aucune nouvelle table n'est nécessaire : le cours partage la plomberie
authored existante (`Activity.guidance`, `AuthoredQuestion`,
`app.authored.service`), déjà pensée pour accueillir un troisième type sans
que le moteur de lecture n'ait à apprendre lequel l'appelle.

## Sous-étapes

1. `01_modele_du_cours.md` : Modèle du cours
2. `02_service_de_composition.md` : Service de composition avec l'examen
3. `03_api_du_cours.md` : API du cours
4. `04_boucle_et_contenu_pilote.md` : Boucle de bout en bout et contenu pilote
5. `05_documentation_cloture.md` : Documentation et clôture

## Conditions de clôture

- migrations upgrade et downgrade validées ;
- Ruff, Mypy et Pytest verts ;
- contrôles d'autorisation et d'isolation validés ;
- vérification qu'aucune réponse au cours n'écrit dans `attempts` ni ne
  modifie une lecture de compétence ;
- documentation et preuves produites, ADR-022 rédigée ;
- commit et push ;
- CI distante réussie ;
- fusion contrôlée vers `main`, une seule Pull Request pour toute l'étape ;
- ETAT et PLANNING mis à jour après preuves.
