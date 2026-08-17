'use client';

import { useState } from 'react';
import { submitAssessment } from '../../lib/actions';
import type { AssessmentQuestion } from '../../lib/types';

/**
 * The whole assessment on one page, submitted once.
 *
 * One submission rather than one request per question: a child on a household
 * tablet should not lose her place to a flaky connection halfway through, and
 * nothing is recorded until she says she has finished.
 *
 * The submit button stays disabled until every question has an answer, and says
 * how many are left. A form that refuses on submission teaches a child that she
 * did something wrong; one that says what remains does not.
 */
export function AssessmentForm({
  assignmentId,
  questions,
}: {
  assignmentId: string;
  questions: AssessmentQuestion[];
}) {
  const [answered, setAnswered] = useState<Record<string, number>>({});
  const [sending, setSending] = useState(false);
  const submit = submitAssessment.bind(null, assignmentId);
  const remaining = questions.length - Object.keys(answered).length;

  return (
    <form action={submit} onSubmit={() => setSending(true)}>
      <ol className="list-unstyled d-flex flex-column gap-3 mb-4">
        {questions.map((question, index) => (
          <li key={question.question_ref}>
            <fieldset className="card border-0 shadow-sm">
              <div className="card-body p-4">
                <legend className="h5 mb-3">
                  <span className="text-secondary me-2">{index + 1}.</span>
                  {question.prompt}
                </legend>
                <div className="d-flex flex-wrap gap-2">
                  {question.choices.map((choice, position) => {
                    const id = `${question.question_ref}-${position}`;
                    return (
                      <div key={id}>
                        <input
                          type="radio"
                          className="btn-check"
                          name={`q:${question.question_ref}`}
                          id={id}
                          value={position}
                          autoComplete="off"
                          onChange={() =>
                            setAnswered((current) => ({
                              ...current,
                              [question.question_ref]: position,
                            }))
                          }
                        />
                        <label className="btn btn-outline-primary btn-lg" htmlFor={id}>
                          {choice}
                        </label>
                      </div>
                    );
                  })}
                </div>
              </div>
            </fieldset>
          </li>
        ))}
      </ol>

      <div className="d-flex flex-wrap align-items-center gap-3">
        <button
          type="submit"
          className="btn btn-success btn-lg"
          disabled={remaining > 0 || sending}
        >
          {sending ? 'Un instant…' : 'J’ai fini'}
        </button>
        <span className="text-secondary" aria-live="polite">
          {remaining > 0
            ? `Encore ${remaining} question${remaining > 1 ? 's' : ''}.`
            : 'Tu peux envoyer.'}
        </span>
      </div>
    </form>
  );
}
