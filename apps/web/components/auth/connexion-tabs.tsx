'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const TABS = [
  { href: '/connexion', label: 'Parent' },
  { href: '/connexion/eleve', label: 'Élève' },
] as const;

/**
 * Le seul endroit qui bascule entre les deux connexions.
 *
 * Les formulaires restent chacun sur sa propre adresse — voir le commentaire
 * de `ParentLoginForm` — pour que le remplissage automatique du navigateur
 * n'attribue jamais l'identifiant de l'un à l'autre. Ce commutateur ne fait
 * que naviguer entre les deux ; rien ici ne les affiche l'un à la place de
 * l'autre sur une même page.
 */
export function ConnexionTabs() {
  const pathname = usePathname();

  return (
    <div className="btn-group mb-4" role="tablist" aria-label="Se connecter en tant que">
      {TABS.map((tab) => {
        const active = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            role="tab"
            aria-selected={active}
            className={`btn ${active ? 'btn-primary' : 'btn-outline-primary'}`}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
