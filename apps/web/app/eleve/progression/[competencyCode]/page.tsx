import Link from 'next/link';
import { api } from '../../../../lib/api';
import { requireChild } from '../../../../lib/session';
import { InterfaceState } from '../../../../components/ui/interface-state';
import { formatDateTime } from '../../../../lib/dates';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../../../lib/types';
import type { Attempt, ChildAssignment, Progress } from '../../../../lib/types';

export const metadata = { title: 'Compétence' };

/**
 * One competency, and what she has already done on it.
 *
 * "What to do next" is not here on purpose: that is a recommendation, and a
 * recommendation is built from the diagnosis — the thing this whole area of
 * the app has never shown a child (see `progression/page.tsx`). What she is
 * shown instead is her own record: every finished attempt that touched this
 * competency, each one a door back to the fuller results it produced.
 */
export default async function CompetencyDetailPage({
  params,
}: {
  params: Promise<{ competencyCode: string }>;
}) {
  await requireChild();
  const { competencyCode } = await params;

  const [progress, attempts, assignments] = await Promise.all([
    api<Progress>('/me/progress'),
    api<Attempt[]>('/me/attempts'),
    api<ChildAssignment[]>('/me/activities'),
  ]);

  const row = progress.ok
    ? progress.data.competencies.find((c) => c.competency_code === competencyCode)
    : undefined;

  if (!row) {
    return (
      <InterfaceState
        kind="empty"
        title="Rien à montrer pour cette compétence"
        description="Elle n’a pas encore été observée dans une activité terminée."
        action={
          <Link href="/eleve/progression" className="btn btn-outline-primary">
            Voir ma progression
          </Link>
        }
      />
    );
  }

  const titleByAssignment = new Map(
    assignments.ok ? assignments.data.map((row) => [row.id, row.activity.title]) : [],
  );

  const touching = (attempts.ok ? attempts.data : [])
    .filter((attempt) => attempt.completed_at !== null)
    .filter((attempt) => attempt.results.some((r) => r.competency_code === competencyCode))
    .sort(
      (a, b) =>
        new Date(b.completed_at ?? 0).getTime() - new Date(a.completed_at ?? 0).getTime(),
    );

  return (
    <>
      <p className="mb-3">
        <Link href="/eleve/progression" className="sc-lien-retour">
          ← Ma progression
        </Link>
      </p>

      <header className="mb-4">
        <span className={OUTCOME_CLASSES[row.latest_outcome]}>
          {OUTCOME_LABELS[row.latest_outcome]}
        </span>
        <h1 className="h3 mt-2 mb-1">{competencyCode}</h1>
        <p className="text-secondary mb-0">{row.explanation}</p>
      </header>

      <h2 className="h6 mb-2">Ce que tu as fait</h2>
      {touching.length === 0 ? (
        <p className="text-secondary small">Rien d’enregistré pour l’instant.</p>
      ) : (
        <ul className="list-group sc-liste-dense">
          {touching.map((attempt) => {
            const result = attempt.results.find(
              (r) => r.competency_code === competencyCode,
            );
            if (!result) return null;
            return (
              <li className="list-group-item" key={attempt.id}>
                <Link href={`/eleve/activites/${attempt.assignment_id}/resultat`}>
                  <span className={OUTCOME_CLASSES[result.outcome]}>
                    {OUTCOME_LABELS[result.outcome]}
                  </span>
                  <span className="fw-semibold text-truncate">
                    {titleByAssignment.get(attempt.assignment_id) ?? 'Activité'}
                  </span>
                  <span className="text-secondary small ms-auto flex-shrink-0">
                    {attempt.completed_at ? formatDateTime(attempt.completed_at) : '—'}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
