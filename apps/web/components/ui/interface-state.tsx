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

const presentation: Record<InterfaceStateKind, { icon: typeof Clock3; className: string; live: 'polite' | 'assertive' }> = {
  loading: { icon: Clock3, className: 'border-secondary-subtle bg-body-tertiary', live: 'polite' },
  empty: { icon: FileQuestion, className: 'border-secondary-subtle bg-body-tertiary', live: 'polite' },
  error: { icon: AlertCircle, className: 'border-danger-subtle bg-danger-subtle', live: 'assertive' },
  success: { icon: CheckCircle2, className: 'border-success-subtle bg-success-subtle', live: 'polite' },
  forbidden: { icon: LockKeyhole, className: 'border-warning-subtle bg-warning-subtle', live: 'assertive' },
  authentication: { icon: LogIn, className: 'border-warning-subtle bg-warning-subtle', live: 'assertive' },
  unavailable: { icon: AlertCircle, className: 'border-secondary-subtle bg-body-tertiary', live: 'polite' },
  offline: { icon: CloudOff, className: 'border-warning-subtle bg-warning-subtle', live: 'assertive' },
};

export function InterfaceState({ kind, title, description, action }: InterfaceStateProps) {
  const state = presentation[kind];
  const Icon = state.icon;

  return (
    <section
      className={`card h-100 border shadow-sm ${state.className}`}
      aria-live={state.live}
      aria-busy={kind === 'loading'}
    >
      <div className="card-body p-4">
        <Icon size={28} className="mb-3" aria-hidden="true" />
        <h2 className="h5">{title}</h2>
        <p className="text-secondary mb-3">{description}</p>
        {action}
      </div>
    </section>
  );
}
