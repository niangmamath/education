'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bell, BookOpen, LineChart, Users, House, Settings } from 'lucide-react';

const items = [
  { href: '/parent', label: 'Accueil', icon: House, exact: true },
  { href: '/parent/enfants', label: 'Enfants', icon: Users },
  { href: '/parent/activites', label: 'Activités', icon: BookOpen },
  { href: '/parent/progression', label: 'Progression', icon: LineChart },
  { href: '/parent/notifications', label: 'Ce qui a changé', icon: Bell },
  { href: '/parent/parametres', label: 'Paramètres', icon: Settings },
];

export function ParentNavigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Navigation Parent" className="sc-parent-nav">
      <ul className="nav nav-pills flex-row flex-lg-column gap-2 mb-0">
        {items.map(({ href, label, icon: Icon, exact }) => {
          const active = exact ? pathname === href : pathname.startsWith(href);
          return (
            <li className="nav-item" key={href}>
              <Link href={href} className={`nav-link d-flex align-items-center gap-2 ${active ? 'active' : ''}`} aria-current={active ? 'page' : undefined}>
                <Icon size={19} aria-hidden="true" /><span>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
