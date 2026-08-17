'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, BookOpen, House } from 'lucide-react';

const items = [
  { href: '/eleve', label: 'Accueil', icon: House, exact: true },
  { href: '/eleve/activites', label: 'Activités', icon: BookOpen },
  { href: '/eleve/progression', label: 'Progression', icon: BarChart3 },
];

export function EleveNavigation() {
  const pathname = usePathname();

  return (
    <nav aria-label="Navigation Élève" className="sc-student-nav">
      <ul className="nav nav-pills flex-row flex-lg-column gap-2 mb-0">
        {items.map(({ href, label, icon: Icon, exact }) => {
          const active = exact ? pathname === href : pathname.startsWith(href);

          return (
            <li className="nav-item" key={href}>
              <Link
                href={href}
                className={`nav-link d-flex align-items-center gap-2 ${active ? 'active' : ''}`}
                aria-current={active ? 'page' : undefined}
              >
                <Icon size={20} aria-hidden="true" />
                <span>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
