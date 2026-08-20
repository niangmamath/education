import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { AssignmentList } from '../../../components/parent/assignment-list';
import type { ParentAssignment } from '../../../lib/types';

export const metadata = { title: 'Activités' };

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
        <AssignmentList assignments={assignments.data} />
      )}
    </>
  );
}
