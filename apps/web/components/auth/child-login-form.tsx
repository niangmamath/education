'use client';

import { useActionState } from 'react';
import { KeyRound } from 'lucide-react';
import { loginChild, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * The child's sign-in, on its own address.
 *
 * Three fields, each naming what it holds so the browser can offer to remember
 * it: the family is an `organization`, the pseudonym is the `username`, the
 * secret code is the password. Sharing an address with the parent's form was
 * what made autofill useless here — one saved credential, two forms, and no way
 * for the browser to know which was which.
 */
export function ChildLoginForm() {
  const [state, action, pending] = useActionState(loginChild, EMPTY);

  return (
    <form action={action} noValidate>
      <span className="sc-feature-icon mb-3" aria-hidden="true">
        <KeyRound size={24} />
      </span>
      <h2 className="h4">Espace Élève</h2>
      <p className="text-secondary">
        Demande le code de ta famille à un adulte. Il ne change pas.
      </p>

      {state.error ? (
        <div className="alert alert-danger" role="alert">
          {state.error}
        </div>
      ) : null}

      <div className="mb-3">
        <label htmlFor="family_code" className="form-label">
          Code de la famille
        </label>
        <input
          id="family_code"
          name="family_code"
          className="form-control text-uppercase"
          autoComplete="organization"
          autoCapitalize="characters"
          spellCheck={false}
          required
        />
      </div>
      <div className="mb-3">
        <label htmlFor="pseudonym" className="form-label">
          Ton pseudo
        </label>
        <input
          id="pseudonym"
          name="pseudonym"
          className="form-control"
          autoComplete="username"
          required
        />
      </div>
      <div className="mb-4">
        <label htmlFor="pin" className="form-label">
          Ton code secret
        </label>
        <input
          id="pin"
          name="pin"
          type="password"
          inputMode="numeric"
          pattern="[0-9]{6}"
          className="form-control"
          autoComplete="current-password"
          required
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={pending}>
        {pending ? 'Connexion…' : 'Entrer'}
      </button>
    </form>
  );
}
