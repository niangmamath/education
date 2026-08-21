'use client';

import { useActionState } from 'react';
import { loginParent, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * One form, on a page of its own.
 *
 * The parent's and the child's sign-in used to share a URL and swap in place
 * behind two tabs. A browser cannot tell two forms at one address apart: it had
 * a single saved credential for the site and filled it into whichever form was
 * showing, which put a parent's password into a child's family code field.
 *
 * A page each is the fix, and it is not a workaround. Signing in as a parent and
 * signing in as a child are different acts with different credentials; giving
 * them one address each lets the browser save and offer the right one, which is
 * what autofill is for.
 *
 * That fix is per-page, and a browser's saved-password store is per-site: with
 * only the child's pseudonym ever saved, Chrome offered it here anyway, into
 * whichever field looked like a login field — `type="email"` was enough of a
 * match. `name="email"` is what the standard `autocomplete="email"` token
 * needs to work for a returning parent, so it stays; the field's `id` is the
 * one Chrome also weighs when it has no stronger signal, so that one moves to
 * something a login-field heuristic won't recognise.
 */
export function ParentLoginForm() {
  const [state, action, pending] = useActionState(loginParent, EMPTY);

  return (
    <form action={action} noValidate>
      <h2 className="h5 mb-4">Se connecter</h2>

      {state.error ? (
        <div className="alert alert-danger" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="mb-3">
        <label htmlFor="parent-email-field" className="form-label">
          Adresse e-mail
        </label>
        <input
          id="parent-email-field"
          name="email"
          type="email"
          className="form-control"
          autoComplete="email"
          required
        />
      </div>
      <div className="mb-4">
        <label htmlFor="password" className="form-label">
          Mot de passe
        </label>
        <input
          id="password"
          name="password"
          type="password"
          className="form-control"
          autoComplete="current-password"
          required
        />
      </div>

      <button type="submit" className="btn btn-primary w-100" disabled={pending}>
        {pending ? 'Connexion…' : 'Se connecter'}
      </button>
    </form>
  );
}
