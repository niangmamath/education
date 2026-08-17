import Link from 'next/link';
import { CheckCircle2 } from 'lucide-react';
import { api } from '../../../../../lib/api';
import { requireChild } from '../../../../../lib/session';
import { InterfaceState } from '../../../../../components/ui/interface-state';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../../../../lib/types';
import type { Attempt } from '../../../../../lib/types';

export const metadata = { title: 'Activité terminée' };

/**
 * What the activity showed, said to the child it is about.
 *
 * Every conclusion carries the sentence the API built from the same counts it
 * stored, so nothing here is a verdict she cannot see the working of. This is
 * her own reading and she is entitled to it — what she is not shown, on any
 * page, is the diagnosis built on top of it.
 *
 * An activity that judged nothing produces no result, and the page says exactly
 * that rather than inventing an encouragement out of an absence.
 */
export default async function ResultatPage({
  params,
}: {
  params: Promise<{ assignmentId: string }>;
}) {
  await requireChild();
  const { assignmentId } = await params;

  const attempts = await api<Attempt[]>(`/me/attempts?assignment_id=${assignmentId}`);
  if (!attempts.ok || attempts.data.length === 0) {
    return (
      <InterfaceState
        kind="empty"
        title="Rien à afficher"
        description="Cette activité n’a pas encore de tentative terminée."
        action={
          <Link href="/eleve/activites" className="btn btn-outline-primary">
            Voir mes activités
          </Link>
        }
      />
    );
  }

  const [latest] = attempts.data;
  const results = latest.results;

  return (
    <>
      <header className="mb-4">
        <span className="sc-feature-icon mb-3 text-success" aria-hidden="true">
          <CheckCircle2 size={28} />
        </span>
        <h1 className="h2 mb-1">C’est terminé</h1>
        <p className="text-secondary mb-0">Voici ce que cette activité a montré.</p>
      </header>

      {results.length === 0 ? (
        <InterfaceState
          kind="empty"
          title="Cette activité n’a rien évalué"
          description="Elle ne disait pas si tes réponses étaient justes, donc rien n’a été conclu."
        />
      ) : (
        <ul className="list-group mb-4">
          {results.map((result) => (
            <li className="list-group-item" key={result.competency_code}>
              <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                <span className={`${OUTCOME_CLASSES[result.outcome]}`}>
                  {OUTCOME_LABELS[result.outcome]}
                </span>
                <span className="fw-semibold">{result.competency_code}</span>
              </div>
              <p className="text-secondary small mb-0">{result.explanation}</p>
            </li>
          ))}
        </ul>
      )}

      <div className="d-flex flex-wrap gap-2">
        <Link href="/eleve" className="btn btn-primary">
          Revenir à l’accueil
        </Link>
        <Link href="/eleve/progression" className="btn btn-outline-primary">
          Voir ma progression
        </Link>
      </div>
    </>
  );
}
