import Link from 'next/link';
import { Clock3 } from 'lucide-react';
import { api } from '../../../lib/api';
import { requireChild } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { StartActivityButton } from '../../../components/eleve/start-activity-button';
import { ActivityHistory } from '../../../components/eleve/activity-history';
import type { ChildAssignment } from '../../../lib/types';

export const metadata = { title: 'Mes activités' };

const LABELS: Record<string, string> = {
  assigned: 'À commencer',
  in_progress: 'En cours',
  completed: 'Terminée',
  cancelled: 'Annulée',
};

/**
 * Everything she has been given, what is owed first.
 *
 * Cancelled assignments are not shown. An activity called off is not something
 * she failed to do, and listing it beside what is owed would read as a reproach.
 */
export default async function MesActivitesPage() {
  await requireChild();
  const assignments = await api<ChildAssignment[]>('/me/activities');

  if (!assignments.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Tes activités n’ont pas pu être chargées"
        description={assignments.message}
      />
    );
  }

  const shown = assignments.data.filter((row) => row.status !== 'cancelled');
  const owed = shown.filter((row) => row.status !== 'completed');
  const done = shown.filter((row) => row.status === 'completed');

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Mes activités</h1>
        <p className="text-secondary mb-0">
          {owed.length > 0
            ? `${owed.length} activité${owed.length > 1 ? 's' : ''} à faire.`
            : 'Tu as tout terminé.'}
        </p>
      </header>

      {shown.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Aucune activité pour l’instant"
          description="Quand un adulte t’en donnera une, elle apparaîtra ici."
        />
      ) : (
        <>
          {owed.length > 0 ? (
            <div className="row g-3">
              {owed.map((row) => (
                <div className="col-12 col-lg-6" key={row.id}>
                  <article className="card h-100 border-0 shadow-sm">
                    <div className="card-body p-4">
                      <span className="mb-2 sc-etat sc-etat-travail">
                        {LABELS[row.status] ?? row.status}
                      </span>
                      <h2 className="h5">{row.activity.title}</h2>
                      {row.note ? (
                        <p className="text-secondary small">{row.note}</p>
                      ) : null}
                      <p className="d-flex align-items-center gap-2 small text-secondary">
                        <Clock3 size={16} aria-hidden="true" />
                        Environ {row.activity.duration_minutes} minutes
                      </p>

                      {row.status === 'assigned' ? (
                        <StartActivityButton assignmentId={row.id} label="Commencer" />
                      ) : null}
                      {row.status === 'in_progress' ? (
                        <Link
                          href={`/eleve/activites/${row.id}`}
                          className="btn btn-primary"
                        >
                          Reprendre
                        </Link>
                      ) : null}
                    </div>
                  </article>
                </div>
              ))}
            </div>
          ) : null}

          <ActivityHistory items={done} />
        </>
      )}
    </>
  );
}
