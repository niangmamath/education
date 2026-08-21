'use client';

import { useActionState } from 'react';
import type { FocusEvent } from 'react';
import { changeParentPassword, updateParentProfile, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

// Même verrou que sur les formulaires de connexion : `autocomplete="current-
// password"` peut se préremplir dès le chargement, sans clic. `new-password`
// (nouveau mot de passe, confirmation) n'a pas ce comportement et n'a donc pas
// besoin du verrou.
function unlock(event: FocusEvent<HTMLInputElement>) {
  event.currentTarget.removeAttribute('readonly');
}

/**
 * Two forms, deliberately not one.
 *
 * A display name and a password carry different risk: a typo in a name costs
 * nothing to fix, a password should never change without proving the one it
 * replaces. Splitting them means neither can be submitted by mistake as a
 * side effect of the other.
 */
export function ProfileControls({ displayName }: { displayName: string }) {
  const [renamed, rename, renaming] = useActionState(updateParentProfile, EMPTY);
  const [changed, change, changing] = useActionState(changeParentPassword, EMPTY);

  return (
    <>
      <section className="card border-0 shadow-sm mb-4">
        <div className="card-body p-4">
          <h2 className="h5 mb-3">Votre nom</h2>

          {renamed.error ? (
            <div className="alert alert-danger" role="alert">
              {renamed.error}
            </div>
          ) : null}

          <form action={rename} className="d-flex flex-wrap align-items-end gap-2">
            <div className="flex-grow-1" style={{ maxWidth: '20rem' }}>
              <label htmlFor="display_name" className="form-label">
                Nom affiché
              </label>
              <input
                id="display_name"
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
        </div>
      </section>

      <section className="card border-0 shadow-sm mb-4">
        <div className="card-body p-4">
          <h2 className="h5 mb-3">Changer de mot de passe</h2>

          {changed.error ? (
            <div className="alert alert-danger" role="alert">
              {changed.error}
            </div>
          ) : null}

          <form
            action={change}
            className="d-flex flex-column gap-2"
            style={{ maxWidth: '20rem' }}
          >
            <div>
              <label htmlFor="current_password" className="form-label">
                Mot de passe actuel
              </label>
              <input
                id="current_password"
                name="current_password"
                type="password"
                className="form-control"
                autoComplete="current-password"
                readOnly
                onFocus={unlock}
                required
              />
            </div>
            <div>
              <label htmlFor="new_password" className="form-label">
                Nouveau mot de passe
              </label>
              <input
                id="new_password"
                name="new_password"
                type="password"
                className="form-control"
                autoComplete="new-password"
                minLength={12}
                required
              />
            </div>
            <div>
              <label htmlFor="confirm_password" className="form-label">
                Confirmer le nouveau mot de passe
              </label>
              <input
                id="confirm_password"
                name="confirm_password"
                type="password"
                className="form-control"
                autoComplete="new-password"
                minLength={12}
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-outline-primary align-self-start"
              disabled={changing}
            >
              {changing ? 'Un instant…' : 'Changer le mot de passe'}
            </button>
          </form>
        </div>
      </section>
    </>
  );
}
