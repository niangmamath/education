import { finishAttempt } from '../../lib/actions';

/**
 * Finishing, as a deliberate act.
 *
 * The content emits a completion statement of its own, and the platform stores
 * it without acting on it: an observation is not a decision. What ends the
 * attempt is a child saying she has finished, here.
 */
export function FinishAttemptButton({
  assignmentId,
  attemptId,
}: {
  assignmentId: string;
  attemptId: string;
}) {
  const finish = finishAttempt.bind(null, assignmentId, attemptId);

  return (
    <form action={finish}>
      <button type="submit" className="btn btn-success btn-lg">
        J’ai terminé
      </button>
    </form>
  );
}
