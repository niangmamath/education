import type { ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Clock3, CloudOff, FileQuestion, LockKeyhole, LogIn } from 'lucide-react';

type InterfaceStateKind =
  | 'loading'
  | 'empty'
  | 'error'
  | 'success'
  | 'forbidden'
  | 'authentication'
  | 'unavailable'
  | 'offline';

type InterfaceStateProps = {
  kind: InterfaceStateKind;
  title: string;
  description: string;
  action?: ReactNode;
};

/**
 * Le rouge est réservé aux pannes.
 *
 * Ces états-là sont tous techniques — un service qui ne répond pas, une session
 * expirée, une liste vide — et aucun ne parle du travail d'un enfant. Le rouge y
 * est donc légitime, à condition qu'il ne serve **qu'**ici : partout où la
 * plateforme parle d'apprentissage, ce qui demande du travail est ocre. Une
 * interface qui emploie la même couleur pour « le serveur est tombé » et pour
 * « cette compétence n'est pas acquise » enseigne à un enfant que la seconde est
 * une avarie.
 *
 * Une session expirée n'est pas non plus une panne : c'est une action à faire,
 * donc ocre.
 */
const presentation: Record<
  InterfaceStateKind,
  { icon: typeof Clock3; className: string; tone: string; live: 'polite' | 'assertive' }
> = {
  loading: { icon: Clock3, className: '', tone: 'text-secondary', live: 'polite' },
  empty: { icon: FileQuestion, className: '', tone: 'text-secondary', live: 'polite' },
  error: { icon: AlertCircle, className: 'sc-etat-ecran-panne', tone: 'text-danger-emphasis', live: 'assertive' },
  success: { icon: CheckCircle2, className: 'sc-etat-ecran-acquis', tone: 'text-success-emphasis', live: 'polite' },
  forbidden: { icon: LockKeyhole, className: 'sc-etat-ecran-travail', tone: 'text-warning-emphasis', live: 'assertive' },
  authentication: { icon: LogIn, className: 'sc-etat-ecran-travail', tone: 'text-warning-emphasis', live: 'assertive' },
  unavailable: { icon: AlertCircle, className: 'sc-etat-ecran-panne', tone: 'text-danger-emphasis', live: 'assertive' },
  offline: { icon: CloudOff, className: 'sc-etat-ecran-travail', tone: 'text-warning-emphasis', live: 'assertive' },
};

export function InterfaceState({ kind, title, description, action }: InterfaceStateProps) {
  const state = presentation[kind];
  const Icon = state.icon;

  return (
    <section
      className={`sc-etat-ecran h-100 ${state.className}`}
      aria-live={state.live}
      aria-busy={kind === 'loading'}
    >
      <div className="p-4">
        <Icon size={26} className={`mb-3 ${state.tone}`} aria-hidden="true" />
        <h2 className="h5">{title}</h2>
        <p className="text-secondary mb-3">{description}</p>
        {action}
      </div>
    </section>
  );
}
