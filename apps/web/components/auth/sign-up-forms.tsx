'use client';

import { useActionState, useState } from 'react';
import { KeyRound, UserPlus } from 'lucide-react';
import { registerChild, registerParent, type FormState } from '../../lib/actions';

const EMPTY: FormState = { error: null };

/**
 * The two sign-up forms.
 *
 * A client component for the tab and the pending state only; what is typed goes
 * to a server action and never to an API address the browser knows.
 *
 * Both forms say their rules **before** they are broken — twelve characters, six
 * digits — rather than after. A form that only objects on submission teaches
 * that you did something wrong; one that says what it wants does not.
 *
 * Every field also names what it holds, so a browser can offer to remember it
 * and fill it next time: the family as an `organization`, the pseudonym as the
 * `username`, the code secret as a new password. A form that has to switch
 * autofill off is a form that failed to describe itself.
 */
export function SignUpForms({ defaultTab }: { defaultTab: 'parent' | 'eleve' }) {
  const [tab, setTab] = useState<'parent' | 'eleve'>(defaultTab);
  const [parentState, parentAction, parentPending] = useActionState(registerParent, EMPTY);
  const [childState, childAction, childPending] = useActionState(registerChild, EMPTY);

  return (
    <div className="card border-0 shadow-sm">
      <div className="card-header bg-body-tertiary border-0 pt-3">
        <ul className="nav nav-tabs card-header-tabs" role="tablist">
          <li className="nav-item" role="presentation">
            <button
              type="button"
              role="tab"
              aria-selected={tab === 'parent'}
              aria-controls="inscription-parent"
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
              aria-controls="inscription-eleve"
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
          <form action={parentAction} id="inscription-parent" role="tabpanel" noValidate>
            <span className="sc-feature-icon mb-3" aria-hidden="true">
              <UserPlus size={24} />
            </span>
            <h2 className="h4">Ouvrir un compte Parent</h2>
            <p className="text-secondary">
              Vous recevrez un code de famille : c’est lui que vos enfants
              utiliseront pour se connecter.
            </p>

            {parentState.error ? (
              <div className="alert alert-danger" role="alert">
                {parentState.error}
              </div>
            ) : null}

            <div className="mb-3">
              <label htmlFor="display_name" className="form-label">
                Votre nom
              </label>
              <input
                id="display_name"
                name="display_name"
                className="form-control"
                autoComplete="name"
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="email-inscription" className="form-label">
                Adresse e-mail
              </label>
              <input
                id="email-inscription"
                name="email"
                type="email"
                className="form-control"
                autoComplete="email"
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="password-inscription" className="form-label">
                Mot de passe
              </label>
              <input
                id="password-inscription"
                name="password"
                type="password"
                className="form-control"
                autoComplete="new-password"
                minLength={12}
                required
                aria-describedby="aide-mot-de-passe"
              />
              <div id="aide-mot-de-passe" className="form-text">
                Au moins douze caractères.
              </div>
            </div>
            <div className="mb-4">
              <label htmlFor="password-confirm" className="form-label">
                Confirmer le mot de passe
              </label>
              <input
                id="password-confirm"
                name="password_confirm"
                type="password"
                className="form-control"
                autoComplete="new-password"
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={parentPending}>
              {parentPending ? 'Création…' : 'Créer le compte'}
            </button>
          </form>
        ) : (
          <form action={childAction} id="inscription-eleve" role="tabpanel" noValidate>
            <span className="sc-feature-icon mb-3" aria-hidden="true">
              <KeyRound size={24} />
            </span>
            <h2 className="h4">Rejoindre ta famille</h2>
            <p className="text-secondary">
              Demande le code de ta famille à un adulte. Ton profil l’attendra :
              il pourra se connecter quand cet adulte l’aura accepté.
            </p>

            {childState.error ? (
              <div className="alert alert-danger" role="alert">
                {childState.error}
              </div>
            ) : null}

            <div className="mb-3">
              <label htmlFor="family_code-inscription" className="form-label">
                Code de la famille
              </label>
              <input
                id="family_code-inscription"
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
              <label htmlFor="display_name-eleve" className="form-label">
                Ton prénom
              </label>
              <input
                id="display_name-eleve"
                name="display_name"
                className="form-control"
                autoComplete="given-name"
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="pseudonym-inscription" className="form-label">
                Le pseudo que tu veux
              </label>
              <input
                id="pseudonym-inscription"
                name="pseudonym"
                className="form-control"
                autoComplete="username"
                minLength={3}
                required
                aria-describedby="aide-pseudo"
              />
              <div id="aide-pseudo" className="form-text">
                Au moins trois lettres. Il doit être différent de celui de tes
                frères et sœurs.
              </div>
            </div>
            <div className="mb-4">
              <label htmlFor="pin-inscription" className="form-label">
                Choisis un code secret
              </label>
              <input
                id="pin-inscription"
                name="pin"
                type="password"
                inputMode="numeric"
                pattern="[0-9]{6}"
                className="form-control"
                autoComplete="new-password"
                required
                aria-describedby="aide-pin"
              />
              <div id="aide-pin" className="form-text">
                Six chiffres. Ne le donne à personne.
              </div>
            </div>

            <button type="submit" className="btn btn-primary" disabled={childPending}>
              {childPending ? 'Création…' : 'Créer mon profil'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
