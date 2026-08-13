# 05.6, définir les états et l’accessibilité

## Objectif

Garantir que le socle visuel ne couvre pas seulement le cas nominal.

## États obligatoires

```text
chargement
vide
erreur
succès
accès refusé
connexion requise
contenu indisponible
réseau dégradé
```

## Contrôles

- ordre de tabulation ;
- focus visible ;
- titres et landmarks ;
- labels et descriptions ;
- messages d’erreur associés aux champs ;
- contraste ;
- zoom navigateur ;
- cibles tactiles ;
- textes alternatifs ;
- responsive mobile, tablette et bureau.

## Preuves

Conserver les résultats dans `docs/ux/validation-accessibilite.md`. Les captures peuvent rester hors de Git si elles sont volumineuses, avec un rapport textuel versionné.

## Acceptation

- [ ] Aucun blocage clavier observé.
- [ ] Focus visible.
- [ ] États annoncés textuellement.
- [ ] Erreurs compréhensibles.
- [ ] Aucune information transmise uniquement par couleur.
