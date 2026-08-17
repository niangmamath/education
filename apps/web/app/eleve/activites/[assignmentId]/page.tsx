import Link from 'next/link';
import { redirect } from 'next/navigation';
import { api } from '../../../../lib/api';
import { requireChild } from '../../../../lib/session';
import { InterfaceState } from '../../../../components/ui/interface-state';
import { ContentPlayer } from '../../../../components/eleve/content-player';
import { FicheForm } from '../../../../components/eleve/fiche-form';
import { StartActivityButton } from '../../../../components/eleve/start-activity-button';
import { FinishAttemptButton } from '../../../../components/eleve/finish-attempt-button';
import type {
  ActivityContent,
  Attempt,
  ChildAssignment,
  Fiche,
} from '../../../../lib/types';

export const metadata = { title: 'Activité' };

/**
 * Doing an activity.
 *
 * The page reads and never writes: the attempt was opened by the act that
 * brought the child here. If she arrives by a bare URL — a bookmark, a shared
 * link — she is offered the button rather than silently having an attempt
 * opened for her by a page load.
 *
 * The content itself is served by another origin, checked ticket by ticket. This
 * page holds the ticket only to pass it to the frame and to the bridge; it never
 * fetches a byte of the content.
 */
export default async function JouerPage({
  params,
}: {
  params: Promise<{ assignmentId: string }>;
}) {
  await requireChild();
  const { assignmentId } = await params;

  const [assignments, attempts] = await Promise.all([
    api<ChildAssignment[]>('/me/activities'),
    api<Attempt[]>(`/me/attempts?assignment_id=${assignmentId}`),
  ]);

  const assignment = assignments.ok
    ? assignments.data.find((row) => row.id === assignmentId)
    : undefined;

  if (!assignment) {
    return (
      <InterfaceState
        kind="empty"
        title="Cette activité n’est pas la tienne"
        description="Elle n’existe pas, ou elle ne t’a pas été donnée."
        action={
          <Link href="/eleve/activites" className="btn btn-outline-primary">
            Voir mes activités
          </Link>
        }
      />
    );
  }

  // An assessment is an activity, but it is not played in a frame: it was
  // written here and it is answered here. Anyone arriving by its assignment URL
  // — a bookmark, the ordinary list — is sent to the page that can ask it.
  if (assignment.activity.kind === 'assessment') {
    redirect('/eleve/examen');
  }

  const running = attempts.ok
    ? attempts.data.find((row) => row.status === 'in_progress')
    : undefined;

  // Une fiche de remédiation est écrite ici, comme l'examen : elle se lit et se
  // répond sur cette page, sans cadre et sans origine de contenu. C'est aussi
  // pourquoi elle fonctionne là où le runtime H5P n'est pas déployé.
  if (assignment.activity.kind === 'remediation') {
    return (
      <FichePage
        assignment={assignment}
        assignmentId={assignmentId}
        attemptId={running?.id ?? null}
      />
    );
  }

  if (!running) {
    return (
      <>
        <h1 className="h3 mb-3">{assignment.activity.title}</h1>
        <InterfaceState
          kind="empty"
          title="Cette activité n’est pas ouverte"
          description={
            assignment.status === 'completed'
              ? 'Tu l’as déjà terminée. Bravo !'
              : 'Appuie sur le bouton pour la commencer.'
          }
          action={
            assignment.status === 'completed' ? (
              <Link href="/eleve/activites" className="btn btn-outline-primary">
                Voir mes activités
              </Link>
            ) : (
              <StartActivityButton assignmentId={assignmentId} label="Commencer" />
            )
          }
        />
      </>
    );
  }

  const content = await api<ActivityContent>(`/me/activities/${assignmentId}/content`);

  return (
    <>
      <header className="mb-3">
        <h1 className="h3 mb-1">{assignment.activity.title}</h1>
        <p className="text-secondary mb-0">
          Environ {assignment.activity.duration_minutes} minutes. Quand tu as fini,
          appuie sur « J’ai terminé ».
        </p>
      </header>

      {content.ok ? (
        <ContentPlayer playUrl={content.data.play_url} />
      ) : (
        <InterfaceState
          kind="unavailable"
          title="Le contenu n’a pas pu être ouvert"
          description={content.message}
        />
      )}

      <div className="mt-4 d-flex flex-wrap gap-2">
        <FinishAttemptButton assignmentId={assignmentId} attemptId={running.id} />
        <Link href="/eleve/activites" className="btn btn-outline-secondary">
          Revenir plus tard
        </Link>
      </div>
    </>
  );
}

/**
 * Une fiche : la leçon d'abord, les questions ensuite.
 *
 * La leçon est visible avant même que la tentative soit ouverte, et elle le
 * reste pendant qu'on répond. Une enfant qui vient d'apprendre qu'elle bute
 * quelque part doit pouvoir relire ce qu'on lui explique autant de fois qu'elle
 * veut, sans que cela ressemble à de la triche : la fiche répare, elle ne
 * mesure pas.
 */
async function FichePage({
  assignment,
  assignmentId,
  attemptId,
}: {
  assignment: ChildAssignment;
  assignmentId: string;
  attemptId: string | null;
}) {
  const fiche = await api<Fiche>(`/me/activities/${assignmentId}/fiche`);

  if (!fiche.ok) {
    return (
      <>
        <h1 className="h3 mb-3">{assignment.activity.title}</h1>
        <InterfaceState
          kind={assignment.status === 'completed' ? 'success' : 'unavailable'}
          title={
            assignment.status === 'completed'
              ? 'Tu l’as déjà terminée'
              : 'Cette fiche n’a pas pu être ouverte'
          }
          description={
            assignment.status === 'completed'
              ? 'Bravo. Tu peux en reprendre une autre quand tu veux.'
              : fiche.message
          }
          action={
            <Link href="/eleve/activites" className="btn btn-outline-primary">
              Voir mes activités
            </Link>
          }
        />
      </>
    );
  }

  return (
    <>
      <header className="mb-4">
        <p className="sc-oeilleton">Pour s’entraîner · environ {fiche.data.duration_minutes} minutes</p>
        <h1 className="mb-0">{fiche.data.title}</h1>
      </header>

      {fiche.data.guidance ? (
        <section className="card sc-student-hero mb-4" aria-labelledby="lecon-title">
          <div className="card-body p-4 p-lg-5">
            <h2 id="lecon-title" className="h5 mb-3">
              Ce qu’il faut retenir
            </h2>
            {fiche.data.guidance.split('\n\n').map((paragraph) => (
              <p className="mb-3" key={paragraph.slice(0, 40)}>
                {paragraph}
              </p>
            ))}
          </div>
        </section>
      ) : null}

      {attemptId ? (
        <>
          <FicheForm attemptId={attemptId} questions={fiche.data.questions} />
          <div className="d-flex flex-wrap gap-2">
            <FinishAttemptButton assignmentId={assignmentId} attemptId={attemptId} />
            <Link href="/eleve/activites" className="btn btn-outline-secondary">
              Revenir plus tard
            </Link>
          </div>
        </>
      ) : (
        <div className="d-flex flex-wrap gap-2">
          <StartActivityButton assignmentId={assignmentId} label="Commencer les questions" />
          <Link href="/eleve/activites" className="btn btn-outline-secondary">
            Revenir plus tard
          </Link>
        </div>
      )}
    </>
  );
}
