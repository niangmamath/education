import Link from 'next/link';
import { AlertTriangle, BookOpen, Sparkles, Users } from 'lucide-react';
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

  const notifications = notificationsFor(active, assignments.ok ? assignments.data : []);

  const masteredTotal = diagnostics.reduce(
    (sum, result) => sum + (result.ok ? (result.data.health?.mastered ?? 0) : 0),
    0,
  );
  const actionableTotal = diagnostics.reduce(
    (sum, result) =>
      sum +
      (result.ok
        ? result.data.localized_gaps.filter((gap) => gap.blocked_by === null).length
        : 0),
    0,
  );
  const inProgressTotal = assignments.ok
    ? assignments.data.filter((row) => row.status === 'assigned' || row.status === 'in_progress')
        .length
    : 0;

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

      {active.length > 0 ? (
        <div className="row g-3 mb-4">
          {[
            { label: 'enfants actifs', value: active.length, icon: Users, tone: 'indigo' as const },
            {
              label: 'compétences acquises',
              value: masteredTotal,
              icon: Sparkles,
              tone: 'acquis' as const,
            },
            {
              label: 'à travailler',
              value: actionableTotal,
              icon: AlertTriangle,
              tone: 'travail' as const,
            },
            {
              label: 'activités en cours',
              value: inProgressTotal,
              icon: BookOpen,
              tone: 'indigo' as const,
            },
          ].map(({ label, value, icon: Icon, tone }) => (
            <div className="col-6 col-lg-3" key={label}>
              <div className="card h-100 border-0 shadow-sm">
                <div className="card-body p-3 p-lg-4">
                  <Icon
                    size={18}
                    aria-hidden="true"
                    className={
                      tone === 'acquis'
                        ? 'text-success-emphasis mb-2'
                        : tone === 'travail'
                          ? 'text-warning-emphasis mb-2'
                          : 'text-primary mb-2'
                    }
                  />
                  <p
                    className={`sc-chiffre-geant mb-0 ${tone === 'acquis' ? 'sc-chiffre-geant-acquis' : tone === 'travail' ? 'sc-chiffre-geant-travail' : ''}`}
                    style={{ fontSize: '1.9rem' }}
                  >
                    {value}
                  </p>
                  <p className="text-secondary small mb-0">{label}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : null}

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
            const deferred =
              diagnostic?.localized_gaps.filter((gap) => gap.blocked_by !== null) ?? [];

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

                    {actionable.length > 0 || deferred.length > 0 ? (
                      <p className="mb-3 d-flex flex-wrap align-items-center gap-2">
                        {actionable.length > 0 ? (
                          <span className="sc-etat sc-etat-travail">
                            <AlertTriangle size={15} aria-hidden="true" />
                            {actionable.length} point{actionable.length > 1 ? 's' : ''} à
                            travailler
                          </span>
                        ) : null}
                        {deferred.length > 0 ? (
                          <span className="text-secondary small">
                            + {deferred.length} en attente d’un prérequis
                          </span>
                        ) : null}
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
