# 04.3, capturer les événements xAPI

## Objectif

Capturer au moins un statement généré par une interaction réelle dans le contenu H5P.

## Principe

H5P expose les événements xAPI via le dispatcher JavaScript. Le statement utile est disponible dans `event.data.statement` lorsque le contenu et le code d’écoute sont servis dans un contexte compatible.

## Preuves attendues

- écouteur enregistré avant l’interaction ;
- événement produit par une action réelle ;
- statement brut conservé ;
- verb, object, result, score et completion analysés selon leur présence ;
- aucune donnée personnelle réelle dans les preuves.

## Jeu minimal de vérification

- événement `attempted`, s’il est émis ;
- événement `answered` ou `completed` ;
- présence du verbe ;
- identifiant de l’objet ;
- score brut et score maximal, s’ils existent ;
- propriété `completion`, si elle existe.

## Ne pas faire

- ne pas inventer un statement ;
- ne pas simuler un événement pour déclarer le spike réussi ;
- ne pas créer encore la table définitive de stockage xAPI ;
- ne pas envoyer les statements vers un LRS externe.

## Acceptation

- [ ] Au moins un événement réel capturé.
- [ ] `event.data.statement` conservé.
- [ ] Interaction source documentée.
- [ ] Données xAPI analysées.
- [ ] Limites propres au type H5P documentées.
