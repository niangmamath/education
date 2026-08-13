# 05.2, définir les routes et la navigation

## Objectif

Produire une architecture de navigation cohérente avant de créer les écrans.

## Livrables

Créer sous `docs/ux/` :

- `routes-mvp.md` ;
- `navigation-parent.md` ;
- `navigation-eleve.md` ;
- `regles-redirection-acces.md`.

## Routes candidates à valider

```text
/
/connexion
/inscription
/aide
/parent
/parent/enfants
/parent/enfants/[studentId]
/parent/activites
/parent/notifications
/parent/parametres
/eleve
/eleve/activites
/eleve/progression
/eleve/recompenses
```

## Contraintes

- Ne pas implémenter encore une protection d’accès fictive.
- Distinguer route publique, future route protégée et route expérimentale.
- Prévoir navigation mobile et bureau.
- Conserver `/health` comme route technique.
- Ne pas exposer l’identifiant réel d’un enfant dans une démonstration.

## Acceptation

- [ ] Chaque route possède un public, un objectif et un état vide.
- [ ] Navigation Parent et Élève séparées.
- [ ] Redirections futures documentées.
- [ ] Aucun lien mort dans le socle visuel implémenté.
