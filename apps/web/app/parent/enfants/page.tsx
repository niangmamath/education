import Link from 'next/link';
import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import type { ChildProfile, ParentProfile } from '../../../lib/types';

export const metadata = { title: 'Mes enfants' };

const STATUS: Record<ChildProfile['status'], { label: string; className: string }> = {
  active: { label: 'Actif', className: 'text-bg-success' },
  pending: { label: 'En attente d’activation', className: 'text-bg-warning' },
  disabled: { label: 'Désactivé', className: 'text-bg-secondary' },
};

/**
 * The family's profiles, and the code that lets a child join it.
 *
 * A pending profile is one a child opened with the family code and that nobody
 * has activated yet. It is shown as waiting rather than as a problem: it is the
 * ordinary way in, and it grants nothing until an adult says so.
 */
export default async function EnfantsPage() {
  await requireParent();
  const [children, parent] = await Promise.all([
    api<ChildProfile[]>('/auth/children'),
    api<ParentProfile>('/auth/me'),
  ]);

  if (!children.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Vos profils enfants n’ont pas pu être chargés"
        description={children.message}
      />
    );
  }

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Mes enfants</h1>
        {parent.ok ? (
          <p className="text-secondary mb-0">
            Code de la famille : <code className="fs-6">{parent.data.family_code}</code>. Un
            enfant en a besoin pour se connecter.
          </p>
        ) : null}
      </header>

      {children.data.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Aucun profil pour l’instant"
          description="Un enfant peut ouvrir son profil avec le code de la famille ; il restera en attente jusqu’à ce que vous l’activiez."
        />
      ) : (
        <ul className="list-group">
          {children.data.map((child) => (
            <li
              className="list-group-item d-flex flex-wrap align-items-center justify-content-between gap-3 py-3"
              key={child.id}
            >
              <div>
                <span className="fw-semibold">{child.display_name}</span>
                <span className="text-secondary small"> — {child.pseudonym}</span>
                <span className={`badge rounded-pill ms-2 ${STATUS[child.status].className}`}>
                  {STATUS[child.status].label}
                </span>
              </div>
              {child.status === 'active' ? (
                <Link
                  href={`/parent/enfants/${child.id}`}
                  className="btn btn-outline-primary btn-sm"
                >
                  Voir sa progression
                </Link>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
