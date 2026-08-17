'use client';

import { useState, useTransition } from 'react';
import { Check, Lightbulb, X } from 'lucide-react';
import { answerFicheQuestion } from '../../lib/actions';
import type { AnswerFeedback, AssessmentQuestion } from '../../lib/types';

/**
 * Une fiche de remédiation, question par question.
 *
 * L'examen d'initiation fait l'inverse — tout part en une fois, sans un mot en
 * retour — et les deux ont raison. Un examen qui répond cesse de mesurer ; une
 * réparation qui ne répond pas est un second contrôle, servi à une enfant à qui
 * on vient d'annoncer une difficulté.
 *
 * Une fois répondue, une question se ferme. Ce n'est pas pour l'empêcher de
 * tricher : c'est parce que la réponse est déjà enregistrée côté serveur, et
 * qu'un bouton qui semble encore actif après coup promet quelque chose qui
 * n'arrivera pas.
 *
 * Rien de rouge nulle part. Une réponse fausse ici n'est pas une panne ni une
 * faute : c'est l'endroit exact où la fiche sert à quelque chose, et elle est
 * marquée en ocre comme tout ce qui se travaille.
 */
export function FicheForm({
  attemptId,
  questions,
}: {
  attemptId: string;
  questions: AssessmentQuestion[];
}) {
  const [said, setSaid] = useState<Record<string, AnswerFeedback>>({});
  const [asking, setAsking] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const answer = (questionRef: string, chosenIndex: number) => {
    setAsking(questionRef);
    startTransition(async () => {
      const feedback = await answerFicheQuestion(attemptId, questionRef, chosenIndex);
      if (feedback) {
        setSaid((current) => ({ ...current, [questionRef]: feedback }));
      }
      setAsking(null);
    });
  };

  const remaining = questions.length - Object.keys(said).length;

  return (
    <div>
      <ol className="list-unstyled d-flex flex-column gap-3 mb-4">
        {questions.map((question, index) => {
          const feedback = said[question.question_ref];
          const busy = pending && asking === question.question_ref;

          return (
            <li key={question.question_ref}>
              <fieldset className="card" disabled={feedback !== undefined || busy}>
                <div className="card-body p-4">
                  <legend className="h5 mb-3">
                    <span className="sc-nombre text-secondary me-2">{index + 1}.</span>
                    {question.prompt}
                  </legend>

                  <div className="d-flex flex-wrap gap-2">
                    {question.choices.map((choice, position) => {
                      const id = `${question.question_ref}-${position}`;
                      return (
                        <button
                          key={id}
                          type="button"
                          className="btn btn-outline-primary btn-lg"
                          onClick={() => answer(question.question_ref, position)}
                        >
                          {choice}
                        </button>
                      );
                    })}
                  </div>

                  {feedback ? (
                    <div
                      className={`mt-3 p-3 sc-etat-ecran ${
                        feedback.correct ? 'sc-etat-ecran-acquis' : 'sc-etat-ecran-travail'
                      }`}
                      role="status"
                    >
                      <p className="d-flex align-items-center gap-2 fw-semibold mb-2">
                        {feedback.correct ? (
                          <>
                            <Check size={18} aria-hidden="true" />
                            C’est ça.
                          </>
                        ) : (
                          <>
                            <X size={18} aria-hidden="true" />
                            Ce n’était pas celle-là.
                          </>
                        )}
                      </p>
                      {feedback.explanation ? (
                        <p className="d-flex gap-2 mb-0">
                          <Lightbulb
                            size={18}
                            aria-hidden="true"
                            className="flex-shrink-0 mt-1"
                          />
                          <span>{feedback.explanation}</span>
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </fieldset>
            </li>
          );
        })}
      </ol>

      <p className="text-secondary" aria-live="polite">
        {remaining > 0
          ? `Encore ${remaining} question${remaining > 1 ? 's' : ''}.`
          : 'Tu as tout fait. Tu peux terminer.'}
      </p>
    </div>
  );
}
