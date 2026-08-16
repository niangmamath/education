import Link from 'next/link';
import { AlertTriangle, Info } from 'lucide-react';
import { api } from '../../../../lib/api';
import { requireParent } from '../../../../lib/session';
import { InterfaceState } from '../../../../components/ui/interface-state';
import { ApplyRemediationButton } from '../../../../components/parent/apply-remediation-button';
import { OUTCOME_CLASSES, OUTCOME_LABELS } from '../../../../lib/types';
import type { ChildProfile, Diagnostic, Progress } from '../../../../lib/types';

export const metadata = { title: 'Progression de l’enfant' };

/**
 * One child, everything the platform proposes about her, and why.
 *
 * Every conclusion on this page carries the sentence that produced it. A parent
 * who cannot argue with a conclusion is only being told what to think, and the
 * project's rules ask for the opposite: an automatic gap is a **candidate**, a
 * root cause is a **hypothesis**, and the score is a summary of readings that
 * are all shown beside it.
 *
 * Deferred gaps are shown apart, with what they are waiting on. Nothing is
 * proposed for them on purpose — working on what buts rather than on what blocks
 * settles neither — and a silence a parent cannot account for would read as an
 * oversight.
 */
export default async function EnfantPage({
  params,
}: {
  params: Promise<{ studentId: string }>;
}) {
  await requireParent();
  const { studentId } = await params;

  const [children, progress, diagnostic] = await Promise.all([
    api<ChildProfile[]>('/auth/children'),
    api<Progress>(`/children/${studentId}/progress`),
    api<Diagnostic>(`/children/${studentId}/diagnostic`),
  ]);

  const child = children.ok
    ? children.data.find((row) => row.id === studentId)
    : undefined;

  if (!child) {
    return (
      <InterfaceState
        kind="empty"
        title="Ce profil n’existe pas"
        description="Il a peut-être été supprimé, ou il n’appartient pas à votre famille."
        action={
          <Link href="/parent/enfants" className="btn btn-outline-primary">
            Revenir à la liste
          </Link>
        }
      />
    );
  }

  if (!diagnostic.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Le diagnostic de cet enfant n’a pas pu être chargé"
        description={diagnostic.message}
      />
    );
  }

  if (!progress.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="La progression de cet enfant n’a pas pu être chargée"
        description={progress.message}
      />
    );
  }

  const { health, localized_gaps, general_gaps, root_causes, recommendations } =
    diagnostic.data;
  const actionable = localized_gaps.filter((gap) => gap.blocked_by === null);
  const deferred = localized_gaps.filter((gap) => gap.blocked_by !== null);

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">{child.display_name}</h1>
        <p className="text-secondary mb-0">
          {progress.data.attempts_completed} activité
          {progress.data.attempts_completed > 1 ? 's terminées' : ' terminée'}.
        </p>
      </header>

      <section className="card border-0 shadow-sm mb-4">
        <div className="card-body p-4">
          <h2 className="h5">Santé académique</h2>
          {health ? (
            <>
              <p className="display-6 fw-bold mb-1">{health.score}</p>
              <p className="text-secondary mb-0">{health.explanation}</p>
            </>
          ) : (
            <p className="text-secondary mb-0">
              Aucune activité terminée : il n’y a rien à résumer, et un zéro dirait
              que le travail s’est mal passé plutôt qu’il n’a pas eu lieu.
            </p>
          )}
        </div>
      </section>

      {!diagnostic.data.tree_available ? (
        <div className="alert alert-secondary d-flex gap-2" role="note">
          <Info size={20} aria-hidden="true" className="flex-shrink-0 mt-1" />
          <span>
            Aucune édition du référentiel n’est en vigueur : les difficultés sont
            listées, mais elles ne sont ni regroupées ni reliées à un prérequis.
          </span>
        </div>
      ) : null}

      <section className="mb-4">
        <h2 className="h4 mb-3">Points d’attention</h2>
        {actionable.length === 0 ? (
          <p className="text-secondary">
            Aucune difficulté à confirmer pour le moment.
          </p>
        ) : (
          <ul className="list-group">
            {actionable.map((gap) => (
              <li className="list-group-item py-3" key={gap.competency_code}>
                <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                  <span className={`badge rounded-pill ${OUTCOME_CLASSES[gap.outcome]}`}>
                    {OUTCOME_LABELS[gap.outcome]}
                  </span>
                  <span className="fw-semibold">
                    {gap.competency_label ?? gap.competency_code}
                  </span>
                </div>
                <p className="text-secondary small mb-0">{gap.explanation}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {deferred.length > 0 ? (
        <section className="mb-4">
          <h2 className="h5 mb-2">Mises de côté pour l’instant</h2>
          <ul className="list-group">
            {deferred.map((gap) => (
              <li className="list-group-item py-3" key={gap.competency_code}>
                <span className="fw-semibold">
                  {gap.competency_label ?? gap.competency_code}
                </span>
                <p className="text-secondary small mb-0">{gap.deferral}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {root_causes.length > 0 ? (
        <section className="mb-4">
          <h2 className="h5 mb-2">Hypothèses</h2>
          {root_causes.map((cause) => (
            <div className="alert alert-warning d-flex gap-2" role="note" key={cause.competency_code}>
              <AlertTriangle size={20} aria-hidden="true" className="flex-shrink-0 mt-1" />
              <span>{cause.explanation}</span>
            </div>
          ))}
        </section>
      ) : null}

      {general_gaps.length > 0 ? (
        <section className="mb-4">
          <h2 className="h5 mb-2">Vues d’ensemble</h2>
          <ul className="list-group">
            {general_gaps.map((general) => (
              <li className="list-group-item py-3" key={general.domain_code}>
                <span className="fw-semibold">{general.domain_label}</span>
                <p className="text-secondary small mb-0">{general.explanation}</p>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="card border-0 shadow-sm mb-4">
        <div className="card-body p-4">
          <h2 className="h5">Activités proposées</h2>
          {recommendations.length === 0 ? (
            <p className="text-secondary mb-0">
              Rien à proposer : soit il n’y a pas de difficulté à travailler, soit
              le catalogue n’a pas d’activité courte pour elle.
            </p>
          ) : (
            <>
              <ul className="list-group list-group-flush mb-3">
                {recommendations.map((recommendation) => (
                  <li className="list-group-item px-0" key={recommendation.activity_code}>
                    <span className="fw-semibold">{recommendation.title}</span>
                    <span className="text-secondary small">
                      {' '}
                      — {recommendation.duration_minutes} minutes
                    </span>
                    <p className="text-secondary small mb-1">{recommendation.reason}</p>
                    <p className="text-secondary small mb-0">{recommendation.proof}</p>
                  </li>
                ))}
              </ul>
              <ApplyRemediationButton childId={studentId} count={recommendations.length} />
              <p className="text-secondary small mt-2 mb-0">
                Rien n’est donné tant que vous ne l’avez pas décidé.
              </p>
            </>
          )}
        </div>
      </section>

      <section>
        <h2 className="h4 mb-3">Toutes les compétences observées</h2>
        {progress.data.competencies.length === 0 ? (
          <p className="text-secondary mb-0">Aucune compétence observée.</p>
        ) : (
          <ul className="list-group">
            {progress.data.competencies.map((row) => (
              <li className="list-group-item py-3" key={row.competency_code}>
                <div className="d-flex flex-wrap align-items-center gap-2 mb-1">
                  <span className={`badge rounded-pill ${OUTCOME_CLASSES[row.latest_outcome]}`}>
                    {OUTCOME_LABELS[row.latest_outcome]}
                  </span>
                  <span className="fw-semibold">{row.competency_code}</span>
                </div>
                <p className="text-secondary small mb-0">{row.explanation}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
