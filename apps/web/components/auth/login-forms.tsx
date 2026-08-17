'use client';

import { useActionState, useState } from 'react';
import { KeyRound, LockKeyhole } from 'lucide-react';
import { loginChild, loginParent, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * The two sign-in forms.
 *
 * A client component only for the tab and the pending state; the credentials go
 * to a server action and never to an API address the browser knows. There is no
 * `fetch` here, and there is nothing in this file a script could read a session
 * from.
 *
 * **Every field says what it is, so the browser can fill it.** Autofill is a
 * feature for the person typing, not a nuisance to switch off — and when it
 * misfires the form is usually to blame. It was here: nothing told the browser
 * what a family code is, so it read the lone text field above a password field
 * as the username and filled it with the six-digit code secret. Naming the three
 * fields properly — the family as an `organization`, the pseudonym as the
 * `username`, the code secret as the password — is what makes the guess
 * unnecessary.
 */
export function LoginForms({ defaultTab }: { defaultTab: 'parent' | 'eleve' }) {
  const [tab, setTab] = useState<'parent' | 'eleve'>(defaultTab);
  const [parentState, parentAction, parentPending] = useActionState(loginParent, EMPTY);
  const [childState, childAction, childPending] = useActionState(loginChild, EMPTY);

  return (
    <div className="card border-0 shadow-sm">
      <div className="card-header bg-body-tertiary border-0 pt-3">
        <ul className="nav nav-tabs card-header-tabs" role="tablist">
          <li className="nav-item" role="presentation">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'parent'}
              aria-controls="panneau-parent"
              className={`nav-link ${tab === 'parent' ? 'active' : ''}`}
              onClick={() => setTab('parent')}
            >
              Je suis un parent
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'eleve'}
              aria-controls="panneau-eleve"
              className={`nav-link ${tab === 'eleve' ? 'active' : ''}`}
              onClick={() => setTab('eleve')}
            >
              Je suis un élève
            </button>
          </li>
        </ul>
      </div>

      <div className="card-body p-4 p-lg-5">
        {tab === 'parent' ? (
          <form action={parentAction} id="panneau-parent" role="tabpanel" noValidate>
            <span className="sc-feature-icon mb-3" aria-hidden="true">
              <LockKeyhole size={24} />
            </span>
            <h2 className="h4">Espace Parent</h2>

            {parentState.error ? (
              <div className="alert alert-danger" role="alert">
                {parentState.error}
              </div>
            ) : null}

            <div className="mb-3">
              <label htmlFor="email" className="form-label">
                Adresse e-mail
              </label>
              <input
                id="email"
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

            <button type="submit" className="btn btn-primary" disabled={parentPending}>
              {parentPending ? 'Connexion…' : 'Se connecter'}
            </button>
          </form>
        ) : (
          <form action={childAction} id="panneau-eleve" role="tabpanel" noValidate>
            <span className="sc-feature-icon mb-3" aria-hidden="true">
              <KeyRound size={24} />
            </span>
            <h2 className="h4">Espace Élève</h2>
            <p className="text-secondary">
              Demande le code de ta famille à un adulte. Il ne change pas.
            </p>

            {childState.error ? (
              <div className="alert alert-danger" role="alert">
                {childState.error}
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
                // The family is the organisation this child belongs to, and
                // naming it as one is what stops the browser guessing. Left to
                // guess, it read the lone text field above a password field as
                // the username and filled it with the six-digit code secret.
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
                pattern="[0-9]*"
                className="form-control"
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={childPending}>
              {childPending ? 'Connexion…' : 'Entrer'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
