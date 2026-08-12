# 04.2, préparer le lecteur H5P Standalone

## Objectif

Rendre un paquet H5P extrait dans un espace expérimental isolé.

## Décision de spike

Utiliser `h5p-standalone` uniquement comme preuve technique. La version doit être verrouillée dans le lockfile. Le paquet H5P doit être extrait avant lecture.

## Contraintes

- Ne pas intégrer immédiatement le lecteur à une route métier définitive.
- Ne pas utiliser `@latest`.
- Ne pas charger les ressources du lecteur depuis un CDN pendant la validation finale.
- Ne pas commiter un paquet dont la licence n’est pas validée.
- Ne pas interpréter l’absence d’erreur de compilation comme une preuve de rendu.

## Preuves attendues

- page locale accessible ;
- contenu visible et interactif ;
- absence d’erreur bloquante dans la console ;
- liste des requêtes réseau échouées ;
- capture d’écran locale conservée dans les preuves, sans données personnelles ;
- navigateur et version documentés.

## Contrôles

```bash
pnpm install --frozen-lockfile
pnpm --filter @studentconnect/web run typecheck
pnpm --filter @studentconnect/web run lint
pnpm --filter @studentconnect/web run build
```

## Intervention possible d’un agent

Un agent peut proposer une architecture de composant dans `experiments/h5p-spike/`, sans modifier `apps/api`, Docker Compose, Alembic, `ETAT.md` ou `PLANNING.md`.

## Acceptation

- [ ] Version du lecteur verrouillée.
- [ ] Paquet extrait sans écrasement de chemin.
- [ ] Rendu visible.
- [ ] Interaction fonctionnelle.
- [ ] Console examinée.
- [ ] Échecs réseau documentés.
