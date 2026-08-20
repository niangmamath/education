import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { api } from '../../../../../../lib/api';
import { requireParent } from '../../../../../../lib/session';
import { InterfaceState } from '../../../../../../components/ui/interface-state';
import { formatDateTime } from '../../../../../../lib/dates';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../../../../../lib/types';
import type { Attempt, ParentAssignment, Progress } from '../../../../../../lib/types';

export const metadata = { title: 'Compétence' };

/**
 * One competency, and what a child has already done on it — the parent's
 * read of the same page her own progression already links to.
 *
 * `Progress` is fetched from `/children/{id}/progress`: the record, not the
 * diagnosis. A parent already has the diagnosis on the child's own page, with
 * every gap and the rule that named it; this page stays what it is on the
 * child's side too, a log of attempts, each linking on to its full results.
 */
export default async function ParentCompetencyDetailPage({
  params,
}: {
  params: Promise<{ studentId: string; competencyCode: string }>;
}) {
  await requireParent();
  const { studentId, competencyCode } = await params;

  const [progress, attempts, assignments] = await Promise.all([
    api<Progress>(`/children/${studentId}/progress`),
    api<Attempt[]>(`/children/${studentId}/attempts`),
    api<ParentAssignment[]>(`/assignments?child_id=${studentId}`),
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
          <Link href="/parent/progression" className="btn btn-outline-primary">
            Voir la progression
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
      <Link href="/parent/progression" className="sc-lien-retour mb-3">
        <ArrowLeft size={18} aria-hidden="true" />
        Progression
      </Link>

      <header className="mb-4">
        <span className={OUTCOME_CLASSES[row.latest_outcome]}>
          {OUTCOME_LABELS[row.latest_outcome]}
        </span>
        <h1 className="h3 mt-2 mb-1">{competencyCode}</h1>
        <p className="text-secondary mb-0">{row.explanation}</p>
      </header>

      <h2 className="h6 mb-2">Ce qui a été fait</h2>
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
                <Link
                  href={`/parent/enfants/${studentId}/activites/${attempt.assignment_id}/resultat`}
                >
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
