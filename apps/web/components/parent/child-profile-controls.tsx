'use client';

import { useActionState } from 'react';
import { resetChildPin, updateChildName, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * A name to rename, a PIN to reset — never a pseudonym here.
 *
 * The pseudonym is what the login route matches, alongside the family code
 * and PIN; a family used to typing one would be locked out by a rename nobody
 * expected. `display_name` costs nothing to change because nothing is matched
 * against it. The PIN reset needs no current PIN: this is the route for one
 * nobody remembers, and the parent's own session is the proof of who is
 * asking — the same route the backend already exercised for step 05.
 */
export function ChildProfileControls({
  childId,
  displayName,
}: {
  childId: string;
  displayName: string;
}) {
  const [renamed, rename, renaming] = useActionState(
    updateChildName.bind(null, childId),
    EMPTY,
  );
  const [reset, resetPin, resetting] = useActionState(
    resetChildPin.bind(null, childId),
    EMPTY,
  );

  return (
    <section className="card mb-4">
      <div className="card-body p-4">
        <p className="sc-oeilleton">Profil</p>

        {renamed.error ? (
          <div className="alert alert-danger" role="alert">
            {renamed.error}
          </div>
        ) : null}

        <form
          action={rename}
          className="d-flex flex-wrap align-items-end gap-2 mb-4"
        >
          <div>
            <label htmlFor={`nom-${childId}`} className="form-label">
              Nom affiché
            </label>
            <input
              id={`nom-${childId}`}
              name="display_name"
              className="form-control"
              defaultValue={displayName}
              required
            />
          </div>
          <button type="submit" className="btn btn-outline-primary" disabled={renaming}>
            {renaming ? 'Un instant…' : 'Enregistrer'}
          </button>
        </form>

        {reset.error ? (
          <div className="alert alert-danger" role="alert">
            {reset.error}
          </div>
        ) : null}

        <form action={resetPin} className="d-flex flex-wrap align-items-end gap-2">
          <div>
            <label htmlFor={`pin-${childId}`} className="form-label">
              Nouveau code secret
            </label>
            <input
              id={`pin-${childId}`}
              name="pin"
              inputMode="numeric"
              pattern="[0-9]{6}"
              maxLength={6}
              className="form-control"
              placeholder="6 chiffres"
              required
            />
          </div>
          <button type="submit" className="btn btn-outline-secondary" disabled={resetting}>
            {resetting ? 'Un instant…' : 'Réinitialiser le code'}
          </button>
        </form>
        <p className="text-secondary small mt-2 mb-0">
          Pour le jour où personne ne s’en souvient. Les connexions ouvertes avec
          l’ancien code sont fermées.
        </p>
      </div>
    </section>
  );
}
