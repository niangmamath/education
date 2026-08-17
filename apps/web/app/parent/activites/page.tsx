import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import type { ParentAssignment } from '../../../lib/types';

export const metadata = { title: 'Activités' };

const LABELS: Record<ParentAssignment['status'], { label: string; className: string }> = {
  assigned: { label: 'Donnée', className: 'sc-etat sc-etat-reporte' },
  in_progress: { label: 'En cours', className: 'sc-etat sc-etat-travail' },
  completed: { label: 'Terminée', className: 'sc-etat sc-etat-acquis' },
  cancelled: { label: 'Annulée', className: 'sc-etat sc-etat-non-acquis' },
};

/**
 * Everything given to the family, newest first.
 *
 * Cancelled assignments are kept in the list rather than hidden: calling an
 * activity off is a decision somebody made, and a history that quietly loses it
 * would answer "was this ever given?" wrongly.
 */
export default async function ParentActivitiesPage() {
  await requireParent();
  const assignments = await api<ParentAssignment[]>('/assignments');

  if (!assignments.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Les activités n’ont pas pu être chargées"
        description={assignments.message}
      />
    );
  }

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Activités</h1>
        <p className="text-secondary mb-0">
          Ce que vous avez donné, et où cela en est.
        </p>
      </header>

      {assignments.data.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Aucune activité donnée"
          description="Les activités proposées apparaissent sur la page de chaque enfant, avec la raison qui les a fait proposer."
        />
      ) : (
        <ul className="list-group">
          {assignments.data.map((assignment) => (
            <li className="list-group-item py-3" key={assignment.id}>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                <span className={LABELS[assignment.status].className}>
                  {LABELS[assignment.status].label}
                </span>
                <span className="fw-semibold">{assignment.activity.title}</span>
                <span className="text-secondary small">
                  — {assignment.child_pseudonym}, {assignment.activity.duration_minutes} minutes
                </span>
              </div>
              {assignment.note ? (
                <p className="text-secondary small mb-0">{assignment.note}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
