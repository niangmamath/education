import Link from 'next/link';
import { AlertTriangle, Users } from 'lucide-react';
import { api } from '../../lib/api';
import { requireParent } from '../../lib/session';
import { InterfaceState } from '../../components/ui/interface-state';
import { notificationsFor } from '../../lib/notifications';
import { NotificationList } from '../../components/parent/notification-list';
import type { ChildProfile, Diagnostic, ParentAssignment } from '../../lib/types';

export const metadata = { title: 'Espace Parent' };

/**
 * What a parent needs before anything else: who, and what deserves attention.
 *
 * Attention points are the diagnostic's, not this page's. It shows the count and
 * the child it concerns, and sends to the page that explains it — a number on a
 * dashboard with no way through to its reasons is exactly the kind of automatic
 * verdict the project refuses.
 *
 * A gap deferred behind a prerequisite is **not** counted as something to act on.
 * It is a real difficulty and it is shown on the child's page, but proposing it
 * here would push a parent towards the very competency the platform has decided
 * not to work on yet.
 */
export default async function ParentHomePage() {
  const session = await requireParent();
  const children = await api<ChildProfile[]>('/auth/children');

  if (!children.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Vos profils enfants n’ont pas pu être chargés"
        description={children.message}
      />
    );
  }

  const active = children.data.filter((child) => child.status === 'active');
  const [assignments, ...diagnostics] = await Promise.all([
    api<ParentAssignment[]>('/assignments'),
    ...active.map((child) => api<Diagnostic>(`/children/${child.id}/diagnostic`)),
  ]);

  const notifications = notificationsFor(
    active,
    assignments.ok ? assignments.data : [],
    diagnostics.map((result, index) => ({
      child: active[index],
      diagnostic: result.ok ? result.data : null,
    })),
  );

  return (
    <>
      <header className="mb-4">
        <p className="sc-oeilleton sc-oeilleton-indigo">Tableau de bord</p>
        <h1 className="mb-1">Bonjour {session.display_name}</h1>
        <p className="text-secondary mb-0">
          {active.length > 0
            ? `${active.length} profil${active.length > 1 ? 's' : ''} actif${active.length > 1 ? 's' : ''}.`
            : 'Aucun profil enfant actif pour le moment.'}
        </p>
      </header>

      {active.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Aucun enfant actif"
          description="Créez un profil, ou activez celui qu’un enfant a ouvert avec votre code famille."
          action={
            <Link href="/parent/enfants" className="btn btn-primary">
              Gérer les profils
            </Link>
          }
        />
      ) : (
        <div className="row g-4 mb-4">
          {active.map((child, index) => {
            const result = diagnostics[index];
            const diagnostic = result.ok ? result.data : null;
            const actionable =
              diagnostic?.localized_gaps.filter((gap) => gap.blocked_by === null) ?? [];

            return (
              <div className="col-12 col-lg-6" key={child.id}>
                <article className="card h-100 border-0 shadow-sm">
                  <div className="card-body p-4">
                    <div className="d-flex align-items-center gap-2 mb-2">
                      <Users size={18} aria-hidden="true" className="text-secondary" />
                      <h2 className="h5 mb-0">{child.display_name}</h2>
                    </div>

                    {diagnostic?.health ? (
                      <p className="text-secondary small mb-3">
                        {diagnostic.health.explanation}
                      </p>
                    ) : (
                      <p className="text-secondary small mb-3">
                        Aucune activité terminée : il n’y a encore rien à lire.
                      </p>
                    )}

                    {actionable.length > 0 ? (
                      <p className="mb-3">
                        <span className="sc-etat sc-etat-travail">
                          <AlertTriangle size={15} aria-hidden="true" />
                          {actionable.length} point{actionable.length > 1 ? 's' : ''} à travailler
                        </span>
                      </p>
                    ) : null}

                    <Link
                      href={`/parent/enfants/${child.id}`}
                      className="btn btn-outline-primary"
                    >
                      Voir le détail
                    </Link>
                  </div>
                </article>
              </div>
            );
          })}
        </div>
      )}

      <section>
        <p className="sc-oeilleton">Depuis trente jours</p>
        <h2 className="h4 mb-3">Ce qui a changé</h2>
        <NotificationList notifications={notifications.slice(0, 5)} />
      </section>
    </>
  );
}
