import { api } from '../../../lib/api';
import { requireParent } from '../../../lib/session';
import { InterfaceState } from '../../../components/ui/interface-state';
import { ProfileControls } from '../../../components/parent/profile-controls';
import type { ParentProfile } from '../../../lib/types';

export const metadata = { title: 'Paramètres et règles' };

type AttemptRule = { code: string; condition: string; outcome: string; description: string };
type DiagnosticRule = {
  code: string;
  condition: string;
  produces: string;
  description: string;
};

/**
 * What the platform decides, and by which rule.
 *
 * The rules are published rather than configurable, and this is the page they
 * were published for. Making them adjustable would mean deciding who may change
 * what an acquired competency means — a decision, not a setting, and one nobody
 * is in a position to take before the Administrateur role of step 15.
 *
 * So there is nothing to turn here, and the page says why instead of showing
 * switches that do nothing.
 */
export default async function ParametresPage() {
  await requireParent();

  const [parent, attemptRules, diagnosticRules] = await Promise.all([
    api<ParentProfile>('/auth/me'),
    api<AttemptRule[]>('/attempts/rules'),
    api<DiagnosticRule[]>('/diagnostic/rules'),
  ]);

  return (
    <>
      <header className="mb-4">
        <h1 className="h2 mb-1">Paramètres et règles</h1>
        <p className="text-secondary mb-0">
          Ce que la plateforme conclut, et à partir de quoi.
        </p>
      </header>

      <section className="card border-0 shadow-sm mb-4">
        <div className="card-body p-4">
          <h2 className="h5">Votre famille</h2>
          {parent.ok ? (
            <>
              <p className="mb-1">{parent.data.display_name}</p>
              <p className="text-secondary mb-0">
                Code de la famille : <code className="fs-6">{parent.data.family_code}</code>
              </p>
            </>
          ) : (
            <p className="text-secondary mb-0">{parent.message}</p>
          )}
        </div>
      </section>

      {parent.ok ? <ProfileControls displayName={parent.data.display_name} /> : null}

      <div className="alert alert-secondary" role="note">
        <strong>Ces règles ne se règlent pas.</strong> Décider du seuil à partir
        duquel une compétence est dite acquise, ou une difficulté nommée, revient
        à décider de ce qui est dit d’un enfant. Elles sont donc publiées ici
        plutôt que confiées à un réglage.
      </div>

      <section className="mb-4">
        <h2 className="h4 mb-3">Comment une activité est lue</h2>
        {attemptRules.ok ? (
          <ul className="list-group">
            {attemptRules.data.map((rule) => (
              <li className="list-group-item py-3" key={rule.code}>
                <p className="fw-semibold mb-1">{rule.condition}</p>
                <p className="text-secondary small mb-0">{rule.description}</p>
              </li>
            ))}
          </ul>
        ) : (
          <InterfaceState
            kind="unavailable"
            title="Les règles n’ont pas pu être chargées"
            description={attemptRules.message}
          />
        )}
      </section>

      <section>
        <h2 className="h4 mb-3">Comment une difficulté est nommée</h2>
        {diagnosticRules.ok ? (
          <ul className="list-group">
            {diagnosticRules.data.map((rule) => (
              <li className="list-group-item py-3" key={rule.code}>
                <p className="fw-semibold mb-1">
                  {rule.condition} <span className="text-secondary">→ {rule.produces}</span>
                </p>
                <p className="text-secondary small mb-0">{rule.description}</p>
              </li>
            ))}
          </ul>
        ) : (
          <InterfaceState
            kind="unavailable"
            title="Les règles n’ont pas pu être chargées"
            description={diagnosticRules.message}
          />
        )}
      </section>
    </>
  );
}
