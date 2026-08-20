import Link from 'next/link';
import { ArrowLeft, Check, CheckCircle2, X } from 'lucide-react';
import { api } from '../../../../../../../lib/api';
import { requireParent } from '../../../../../../../lib/session';
import { InterfaceState } from '../../../../../../../components/ui/interface-state';
import { formatDateTime } from '../../../../../../../lib/dates';
import { readableResponse } from '../../../../../../../lib/xapi';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../../../../../../lib/types';
import type { Attempt } from '../../../../../../../lib/types';

export const metadata = { title: 'Résultats' };

/**
 * The parent's read of one attempt — the door `attempts.py` opened once the
 * assignment listing had a "Terminée" nothing led anywhere from.
 *
 * Same shape as the child's own results page on purpose: a parent reading
 * what her child read should not have to learn a second layout to do it.
 */
export default async function ParentResultatPage({
  params,
}: {
  params: Promise<{ studentId: string; assignmentId: string }>;
}) {
  await requireParent();
  const { studentId, assignmentId } = await params;

  const attempts = await api<Attempt[]>(
    `/children/${studentId}/attempts?assignment_id=${assignmentId}`,
  );

  if (!attempts.ok || attempts.data.length === 0) {
    return (
      <InterfaceState
        kind="empty"
        title="Rien à afficher"
        description="Cette activité n’a pas encore de tentative terminée."
        action={
          <Link href="/parent/activites" className="btn btn-outline-primary">
            Voir les activités
          </Link>
        }
      />
    );
  }

  const completed = attempts.data.filter((row) => row.completed_at !== null);
  const latest: Attempt = completed.length > 0 ? completed[0] : attempts.data[0];
  const results = latest.results;

  return (
    <>
      <Link href="/parent/activites" className="sc-lien-retour mb-3">
        <ArrowLeft size={18} aria-hidden="true" />
        Toutes les activités
      </Link>

      <header className="mb-4">
        <span className="sc-feature-icon mb-3 text-success" aria-hidden="true">
          <CheckCircle2 size={28} />
        </span>
        <h1 className="h2 mb-1">C’est terminé</h1>
        <p className="text-secondary mb-0">
          {latest.completed_at
            ? `Terminée le ${formatDateTime(latest.completed_at)}.`
            : 'Voici ce que cette activité a montré.'}
        </p>
      </header>

      {results.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Cette activité n’a rien évalué"
          description="Elle ne disait pas si les réponses étaient justes, donc rien n’a été conclu."
        />
      ) : (
        <ul className="list-group mb-4">
          {results.map((result) => (
            <li className="list-group-item" key={result.competency_code}>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                <span className={OUTCOME_CLASSES[result.outcome]}>
                  {OUTCOME_LABELS[result.outcome]}
                </span>
                <span className="fw-semibold">{result.competency_code}</span>
              </div>
              <p className="text-secondary small mb-0">{result.explanation}</p>
            </li>
          ))}
        </ul>
      )}

      {latest.responses.length > 0 ? (
        <>
          <h2 className="h6 mb-2">Détail des réponses</h2>
          <ul className="list-group sc-liste-dense mb-4">
            {latest.responses.map((response, index) => (
              <li className="list-group-item" key={response.id}>
                {response.is_correct === true ? (
                  <Check
                    size={16}
                    aria-hidden="true"
                    className="text-success flex-shrink-0"
                  />
                ) : response.is_correct === false ? (
                  <X size={16} aria-hidden="true" className="text-secondary flex-shrink-0" />
                ) : (
                  <span className="flex-shrink-0" style={{ width: 16 }} aria-hidden="true" />
                )}
                <span className="text-secondary small flex-shrink-0">{index + 1}.</span>
                <span className="text-truncate">
                  {response.response ? readableResponse(response.response) : '—'}
                </span>
              </li>
            ))}
          </ul>
        </>
      ) : null}

      <div className="d-flex flex-wrap gap-2">
        <Link href={`/parent/enfants/${studentId}`} className="btn btn-primary">
          Voir le diagnostic
        </Link>
        <Link href="/parent/activites" className="btn btn-outline-primary">
          Toutes les activités
        </Link>
      </div>
    </>
  );
}
