import Link from 'next/link';
import { AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react';

type CheckStatus = 'passed' | 'failed' | 'warning';
type OverallStatus = 'loading' | 'healthy' | 'degraded' | 'unhealthy';
type HealthCheck = { name: string; status: CheckStatus; message: string };

const simulatedChecks: HealthCheck[] = [
  { name: 'Frontend Build', status: 'passed', message: 'Application Next.js compilée avec succès' },
  { name: 'Compilation TypeScript', status: 'passed', message: 'Aucune erreur de type détectée' },
  { name: 'Styles du frontend', status: 'passed', message: 'Bootstrap et les styles temporaires sont traités correctement' },
  { name: 'Configuration de l’environnement', status: 'passed', message: 'Configuration de développement chargée' },
  { name: 'Installation des dépendances', status: 'passed', message: 'Dépendances du frontend installées' },
];

const checkPresentation: Record<CheckStatus, { row: string; badge: string; label: string }> = {
  passed: { row: 'border-success-subtle bg-success-subtle', badge: 'text-bg-success', label: 'Réussi' },
  warning: { row: 'border-warning-subtle bg-warning-subtle', badge: 'text-bg-warning', label: 'Avertissement' },
  failed: { row: 'border-danger-subtle bg-danger-subtle', badge: 'text-bg-danger', label: 'Échec' },
};

function CheckIcon({ status }: { status: CheckStatus }) {
  if (status === 'passed') return <CheckCircle2 size={22} className="text-success" aria-hidden="true" />;
  if (status === 'warning') return <AlertCircle size={22} className="text-warning-emphasis" aria-hidden="true" />;
  return <XCircle size={22} className="text-danger" aria-hidden="true" />;
}

function getOverallStatus(checks: HealthCheck[]): OverallStatus {
  if (checks.some((check) => check.status === 'failed')) {
    return 'unhealthy';
  }

  if (checks.some((check) => check.status === 'warning')) {
    return 'degraded';
  }

  return 'healthy';
}

export default function HealthCheckPage() {
  const checks = simulatedChecks;
  const status = getOverallStatus(checks);

  const overall = {
    loading: { title: 'Chargement des vérifications', description: 'Veuillez patienter.', panel: 'border-secondary-subtle', icon: <Clock size={30} className="text-secondary" aria-hidden="true" /> },
    healthy: { title: 'Tous les services sont opérationnels', description: 'Le frontend StudentConnect fonctionne normalement.', panel: 'border-success', icon: <CheckCircle2 size={30} className="text-success" aria-hidden="true" /> },
    degraded: { title: 'Certains services sont dégradés', description: 'Le frontend fonctionne avec des avertissements.', panel: 'border-warning', icon: <AlertCircle size={30} className="text-warning-emphasis" aria-hidden="true" /> },
    unhealthy: { title: 'Services non disponibles', description: 'Le frontend rencontre un problème critique.', panel: 'border-danger', icon: <XCircle size={30} className="text-danger" aria-hidden="true" /> },
  }[status];

  const counts = {
    passed: checks.filter((check) => check.status === 'passed').length,
    warning: checks.filter((check) => check.status === 'warning').length,
    failed: checks.filter((check) => check.status === 'failed').length,
  };

  return (
    <div className="d-flex min-vh-100 flex-column bg-body-tertiary">
      <header className="border-bottom bg-white">
        <div className="container py-3 d-flex align-items-center justify-content-between gap-3">
          <Link href="/" className="d-inline-flex align-items-center gap-3 text-decoration-none">
            <span className="sc-brand-mark" aria-hidden="true">SC</span>
            <span><span className="d-block fw-bold text-dark">StudentConnect</span><span className="d-block small text-secondary">Vérification technique</span></span>
          </Link>
          <span className="badge text-bg-secondary">Prototype</span>
        </div>
      </header>

      <main className="container flex-grow-1 py-5">
        <div className="text-center mb-5">
          <p className="sc-oeilleton sc-oeilleton-indigo">Diagnostic local</p>
          <h1 className="display-5 fw-bold">État de santé</h1>
          <p className="lead text-secondary mb-0">{status === 'loading' ? 'Chargement…' : 'StudentConnect Frontend'}</p>
        </div>

        <section className={`card border-start border-4 shadow-sm mb-4 ${overall.panel}`} aria-live="polite" aria-busy={status === 'loading'}>
          <div className="card-body p-4 d-flex align-items-start gap-3">
            <span className="sc-health-icon" aria-hidden="true">{overall.icon}</span>
            <div><h2 className="h4 mb-1">{overall.title}</h2><p className="text-secondary mb-0">{overall.description}</p></div>
          </div>
        </section>

        <section className="card border-0 shadow-sm mb-4" aria-labelledby="checks-title">
          <div className="card-body p-4">
            <h2 id="checks-title" className="h4 mb-4">Vérifications détaillées</h2>
            {status === 'loading' ? (
              <div className="d-flex align-items-center gap-3" role="status"><span className="spinner-border text-primary" aria-hidden="true" /><span>Vérification en cours…</span></div>
            ) : (
              <div className="vstack gap-3">
                {checks.map((check) => {
                  const presentation = checkPresentation[check.status];
                  return (
                    <article key={check.name} className={`border rounded-3 p-3 d-flex flex-column flex-sm-row align-items-sm-center gap-3 ${presentation.row}`}>
                      <CheckIcon status={check.status} />
                      <div className="flex-grow-1"><h3 className="h6 mb-1">{check.name}</h3><p className="small text-secondary mb-0">{check.message}</p></div>
                      <span className={`badge ${presentation.badge}`}>{presentation.label}</span>
                    </article>
                  );
                })}
              </div>
            )}
          </div>
        </section>

        {status !== 'loading' && (
          <section className="card border-0 shadow-sm" aria-labelledby="summary-title">
            <div className="card-body p-4">
              <h2 id="summary-title" className="h4 mb-4">Résumé</h2>
              <div className="row g-3 text-center">
                <div className="col-12 col-sm-4"><div className="border rounded-3 p-3"><strong className="d-block display-6 sc-nombre text-success">{counts.passed}</strong><span>Réussis</span></div></div>
                <div className="col-12 col-sm-4"><div className="border rounded-3 p-3"><strong className="d-block display-6 sc-nombre text-warning-emphasis">{counts.warning}</strong><span>Avertissements</span></div></div>
                <div className="col-12 col-sm-4"><div className="border rounded-3 p-3"><strong className="d-block display-6 sc-nombre text-danger">{counts.failed}</strong><span>Échecs</span></div></div>
              </div>
            </div>
          </section>
        )}

        <div className="text-center small text-secondary mt-5"><p className="mb-1">Dernière vérification : session actuelle</p><p className="mb-0">Environnement : développement</p></div>
      </main>
    </div>
  );
}
