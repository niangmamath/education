import Link from 'next/link';
import { ArrowRight, Clock3, Sparkles } from 'lucide-react';
import { api } from '../../lib/api';
import { requireChild } from '../../lib/session';
import { InterfaceState } from '../../components/ui/interface-state';
import { StartActivityButton } from '../../components/eleve/start-activity-button';
import type { ChildAssignment, NextSteps, Progress } from '../../lib/types';

export const metadata = { title: 'Espace Élève' };

/**
 * What a child sees first: one thing to do, and how she is getting on.
 *
 * The activity under way comes before anything else. Something half-finished is
 * the only item on this page that is genuinely urgent, and burying it under a
 * list of what is left would be the surest way to leave it unfinished.
 *
 * There is no diagnosis anywhere here, and that is the design rather than an
 * omission: no gap, no score, no rule name. What she is offered are activities
 * and how long they take. Her own results and progress remain hers to read, and
 * each explains itself.
 */
export default async function EleveHomePage() {
  const session = await requireChild();
  const [assignments, steps, progress] = await Promise.all([
    api<ChildAssignment[]>('/me/activities'),
    api<NextSteps>('/me/next-steps'),
    api<Progress>('/me/progress'),
  ]);

  if (!assignments.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Tes activités n’ont pas pu être chargées"
        description={assignments.message}
      />
    );
  }

  const owed = assignments.data.filter(
    (row) => row.status === 'assigned' || row.status === 'in_progress',
  );
  const underWay = owed.find((row) => row.status === 'in_progress');
  const next = owed.find((row) => row.status === 'assigned');
  const featured = underWay ?? next;
  const mastered =
    progress.ok
      ? progress.data.competencies.filter((row) => row.latest_outcome === 'mastered').length
      : 0;

  return (
    <>
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Accueil Élève</p>
        <h1 className="h2 mb-2">Bonjour, {session.display_name}</h1>
        <p className="text-secondary mb-0">
          {featured
            ? 'Voici ce que tu peux faire maintenant.'
            : 'Tu n’as rien à faire pour le moment.'}
        </p>
      </header>

      {featured ? (
        <section className="card border-0 shadow-sm sc-student-hero mb-4">
          <div className="card-body p-4 p-lg-5">
            <span className="badge rounded-pill text-bg-primary mb-3">
              {underWay ? 'À reprendre' : 'À commencer'}
            </span>
            <h2 className="h3">{featured.activity.title}</h2>
            {featured.note ? <p className="text-secondary mb-3">{featured.note}</p> : null}
            <div className="d-flex align-items-center gap-2 small text-secondary mb-4">
              <Clock3 size={18} aria-hidden="true" />
              <span>Environ {featured.activity.duration_minutes} minutes</span>
            </div>
            {underWay ? (
              <Link
                href={`/eleve/activites/${featured.id}`}
                className="btn btn-primary btn-lg"
              >
                Reprendre <ArrowRight size={19} aria-hidden="true" />
              </Link>
            ) : (
              <StartActivityButton assignmentId={featured.id} label="Commencer" />
            )}
          </div>
        </section>
      ) : (
        <InterfaceState
          kind="empty"
          title="Rien à faire pour l’instant"
          description="Quand un adulte te donnera une activité, elle apparaîtra ici."
          action={
            <Link href="/eleve/progression" className="btn btn-outline-primary">
              Voir ma progression
            </Link>
          }
        />
      )}

      <div className="row g-4 mt-1">
        <div className="col-12 col-md-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <h2 className="h5">Ma progression</h2>
              <p className="text-secondary mb-3">
                {progress.ok && progress.data.attempts_completed > 0
                  ? `${progress.data.attempts_completed} activité${
                      progress.data.attempts_completed > 1 ? 's terminées' : ' terminée'
                    }, ${mastered} compétence${mastered > 1 ? 's acquises' : ' acquise'}.`
                  : 'Tu verras ici ce que tu as déjà réussi.'}
              </p>
              <Link href="/eleve/progression" className="btn btn-outline-primary">
                Voir le détail
              </Link>
            </div>
          </section>
        </div>

        <div className="col-12 col-md-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <Sparkles className="text-warning-emphasis mb-3" aria-hidden="true" />
              <h2 className="h5">Pour t’entraîner</h2>
              {steps.ok && steps.data.steps.length > 0 ? (
                <ul className="list-unstyled mb-0">
                  {steps.data.steps.map((step) => (
                    <li key={step.activity_code} className="mb-2">
                      <span className="fw-semibold">{step.title}</span>
                      <span className="text-secondary small">
                        {' '}
                        — {step.duration_minutes} minutes
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-secondary mb-0">
                  Rien de particulier à retravailler pour l’instant.
                </p>
              )}
            </div>
          </section>
        </div>
      </div>
    </>
  );
}
