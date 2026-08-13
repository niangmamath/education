# Validation manuelle dans le navigateur

- Date : 12 août 2026
- URL : `http://127.0.0.1:4174/`
- Navigateur : Microsoft Edge sous Windows, accès au serveur WSL via `127.0.0.1`
- Contenu : `H5P.TrueFalse 1.8`

## Observations

- [x] La page du spike est accessible.
- [x] Le lecteur H5P est initialisé.
- [x] La question « Oslo is the capital of Norway. » est visible.
- [x] Les réponses `Yes` et `No` sont visibles.
- [x] L’image intégrée est visible.
- [x] La réponse `Yes` peut être sélectionnée.
- [x] Le contrôle de la réponse fonctionne.
- [x] Le résultat `1/1` est affiché.
- [x] Le message `You got 1 out of 1 points` est affiché.
- [x] `Rights of use` est accessible.
- [x] Les assets de `H5P.Components` répondent `200` après correction.
- [x] Aucun CDN externe n’est requis pour le rendu observé.

## Réserve

La capture xAPI n’est pas encore validée. Le rendu actuel reste une preuve locale expérimentale.
