import Link from 'next/link';
import { api } from '../../../lib/api';
import { requireChild } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { AssessmentForm } from '../../../components/eleve/assessment-form';
import type { Assessment } from '../../../lib/types';

export const metadata = { title: 'Pour faire connaissance' };

/**
 * The first thing a new child does, and the only one the platform gives her.
 *
 * It is written to be entered without apprehension: no timer, no score, no
 * mention of a level, and a title that says what it is for. A six-year-old
 * meeting a page called "évaluation diagnostique" learns something about school
 * before she learns anything about herself.
 */
export default async function ExamenPage() {
  await requireChild();
  const assessment = await api<Assessment>('/me/assessment');

  if (!assessment.ok) {
    return (
      <InterfaceState
        kind="unavailable"
        title="Ce n’est pas disponible pour l’instant"
        description={assessment.message}
      />
    );
  }

  const { done, assignment_id, title, questions } = assessment.data;

  if (assignment_id === null || questions.length === 0) {
    return (
      <InterfaceState
        kind={done ? 'success' : 'empty'}
        title={done ? 'Tu l’as déjà fait' : 'Rien à faire ici pour l’instant'}
        description={
          done
            ? 'Merci ! Ce que tu as montré est dans ta progression.'
            : 'Reviens plus tard, ou regarde tes activités.'
        }
        action={
          <Link href={done ? '/eleve/progression' : '/eleve'} className="btn btn-primary">
            {done ? 'Voir ma progression' : 'Revenir à l’accueil'}
          </Link>
        }
      />
    );
  }

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">{title}</h1>
        <p className="text-secondary mb-0">
          Douze petites questions pour savoir par où commencer. Ce n’est pas noté,
          et personne ne te compare à qui que ce soit. Si tu ne sais pas, choisis
          ce que tu penses.
        </p>
      </header>

      <AssessmentForm assignmentId={assignment_id} questions={questions} />
    </>
  );
}
