# ADR-005 : Stratégie CK-12, Khan Academy et PhET

| Attribut | Valeur |
|---|---|
| **Statut** | Accepted |
| **Date** | 2026-08-07 |
| **Décideurs** | Équipe stage StudentConnect |
| **Issue GitHub** | — |

## Contexte

Les benchmarks et tests manuels documentés dans `steps/etat.md` confirment :

- absence d’API publique générale clairement documentée pour Khan Academy et CK-12 dans le périmètre étudié ;
- embed CK-12 fonctionnel mais avec redirection possible vers CK-12 ;
- PhET pertinent pour simulations avec quiz interne StudentConnect.

StudentConnect ne doit pas reproduire ces plateformes ; il les utilise comme ressources externes tout en conservant le dossier longitudinal.

## Décision

| Fournisseur | Mode V0.1 | Suivi |
|---|---|---|
| **CK-12** | Lien ou embed officiel ; `launch-only` ou `internal-wrapper` | Quiz interne après activité ; pas de sync progression CK-12 |
| **Khan Academy / Khan Academy Kids** | Liens contrôlés depuis le catalogue | `launch-only` ; jamais de sync complète supposée |
| **PhET** | Simulation externe (lien/embed) | Quiz interne StudentConnect après session |

Aucune API non officielle ne devient une dépendance critique.

## Options étudiées

| Option | Avantages | Inconvénients |
|---|---|---|
| **Liens / embeds + wrapper interne** (retenue) | Conforme conditions d’usage, rapide | Suivi limité côté fournisseur |
| Scraping / API non documentée | Données riches | Interdit par règles projet, fragile, risque légal |
| Réhébergement contenu | Contrôle total | Violation licences probables |
| Exclusion totale des externes | Simplicité | Perte valeur démo remédiation |

## Conséquences

- Chaque ressource externe est cataloguée avec : fournisseur, URL, licence, langue, niveau, matière, compétence, mode d’accès, mode de suivi, date de vérification, statut éditorial.
- Le fichier `index.html` à la racine constitue un spike CK-12 précoce (embed assessment).
- Spike formalisé à l’étape `04_catalogue_et_integrations/03_spike_ck12_khan_phet.md`.

## Risques

| Risque | Niveau | Atténuation |
|---|---|---|
| Redirection CK-12 hors parcours | P2 | Wrapper interne + quiz interne |
| Contenu externe indisponible le jour de la démo | P2 | Catalogue avec ressources de repli |
| Confusion parent sur suivi progression Khan | P3 | Libellés clairs « ouverture externe » |

## Références

- `steps/etat.md` — Tests CK-12, Khan, absence API
- `steps/PROMPT_GENERAL.md` §7
- `index.html` — spike embed CK-12
