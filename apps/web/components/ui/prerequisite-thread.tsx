import type { ReactNode } from 'react';

/**
 * Le fil de prérequis : le raisonnement de la plateforme, rendu visible.
 *
 * Ce que ce produit fait et qu'un carnet de notes ne fait pas : quand une
 * compétence coince, il regarde ce dont elle dépend, et si le prérequis n'est
 * pas assuré, c'est **celui-là** qu'il fait travailler. Demander une
 * soustraction à une enfant qui ne dénombre pas encore, c'est lui demander
 * d'échouer une deuxième fois au même endroit.
 *
 * Le fil dessine cette dépendance : un nœud par compétence, un trait entre deux
 * nœuds là où la relation existe vraiment. Ce n'est pas une numérotation posée
 * sur une liste quelconque — s'il n'y a pas de prérequis, il n'y a pas de fil.
 *
 * Trois états, distingués par la forme autant que par la couleur, pour que la
 * lecture tienne aussi sans les couleurs : plein pour ce qui est acquis, plein
 * et cerclé pour ce qu'on travaille maintenant, creux et pointillé pour ce qui
 * est reporté derrière son prérequis.
 */

export type LinkState = 'acquis' | 'travail' | 'reporte' | 'neutre';

export type ThreadLink = {
  title: string;
  note?: ReactNode;
  state: LinkState;
  /** Ce que la plateforme fait de ce maillon, dit en clair. */
  verdict?: string;
};

const VERDICT_CLASS: Record<LinkState, string> = {
  acquis: 'sc-etat sc-etat-acquis',
  travail: 'sc-etat sc-etat-travail',
  reporte: 'sc-etat sc-etat-reporte',
  neutre: 'sc-etat sc-etat-reporte',
};

export function PrerequisiteThread({
  links,
  label,
}: {
  links: ThreadLink[];
  label: string;
}) {
  if (links.length === 0) {
    return null;
  }

  return (
    <ol className="sc-fil" aria-label={label}>
      {links.map((link) => (
        <li className="sc-fil-maillon" data-etat={link.state} key={link.title}>
          <p className="sc-fil-titre">{link.title}</p>
          {link.verdict ? (
            <p className="mb-1">
              <span className={VERDICT_CLASS[link.state]}>{link.verdict}</span>
            </p>
          ) : null}
          {link.note ? <p className="sc-fil-note">{link.note}</p> : null}
        </li>
      ))}
    </ol>
  );
}
