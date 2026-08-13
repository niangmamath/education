# Rapport de validation de la capture xAPI

## Métadonnées

- Étape : `04_spike_h5p_critique`
- Sous-étape : `03_capturer_evenements_xapi`
- Date : 12 août 2026
- Branche : `spike/h5p-critical`
- Statut : **Terminé pour le paquet pilote True/False**

## Scénario exécuté

1. Chargement du paquet pilote `H5P.TrueFalse 1.8` dans H5P Standalone.
2. Activation de l’écouteur `H5P.externalDispatcher.on('xAPI', handler)` après l’initialisation du lecteur.
3. Sélection de la réponse `Yes`.
4. Activation du bouton `Check`.
5. Affichage du score `1/1`.
6. Capture et téléchargement du dernier statement xAPI réel.

## Événements observés

- Un événement `attempted` a été observé avant la réponse.
- Trois événements ont été reçus pendant le scénario complet.
- Le dernier événement capturé est `answered`.

## Statement validé

- Type de preuve : événement xAPI réel produit par H5P.
- Verbe : `http://adlnet.gov/expapi/verbs/answered`.
- Objet : `https://studentconnect.local/h5p/truefalse-oslo-001`.
- Type d’interaction : `true-false`.
- Bibliothèque : `http://h5p.org/libraries/H5P.TrueFalse-1.8`.
- Réponse : `true`.
- Score brut : `1`.
- Score maximal : `1`.
- Score normalisé : `1`.
- Succès : `true`.
- Complétion : `true`.
- Durée : `PT227.97S`.
- Acteur : identifiant pseudonyme au format UUID.
- Timestamp source : absent du statement produit par H5P.

## Traitement du timestamp

Le statement original est conservé sans modification. Le validateur accepte l’absence du timestamp source et enregistre séparément `validatedAtUtc`, qui date uniquement la validation de la preuve. Cette date ne doit pas être interprétée comme l’heure de l’interaction H5P.

## Validation automatique

Le validateur vérifie :

- la structure de l’acteur ;
- le caractère pseudonyme de son identifiant ;
- le verbe `answered` ;
- l’IRI StudentConnect ;
- le type `true-false` ;
- la catégorie `H5P.TrueFalse-1.8` ;
- la réponse ;
- le score `1/1` ;
- le succès et la complétion ;
- la durée ;
- l’absence de paquet `.h5p` suivi par Git.

## Décision

La capture d’un événement xAPI réel depuis `H5P.TrueFalse 1.8` est validée pour le spike StudentConnect. Cette preuve démontre que StudentConnect peut écouter localement les événements H5P et récupérer un résultat exploitable sans LRS externe.

## Limites

- Aucun stockage backend n’est implémenté à ce stade.
- Aucun envoi vers un LRS n’est effectué.
- La validation porte uniquement sur le type True/False pilote.
- L’acteur pseudonyme est généré par le runtime expérimental et n’est pas encore relié à un utilisateur StudentConnect.
- La politique définitive de timestamp sera traitée lors de la conception de l’endpoint de collecte.

## Prochaine sous-étape

Analyser la compatibilité, la sécurité et les limites du spike, puis préparer la décision de périmètre H5P.
