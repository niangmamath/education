import Link from 'next/link';
import { AlertTriangle, ArrowRight, BookOpen, TrendingUp } from 'lucide-react';
import { PrototypeNotice } from '../../components/ui/prototype-notice';

export const metadata = { title: 'Espace Parent' };

export default function ParentDashboardPage() {
  return (
    <>
      <PrototypeNotice />
      <div className="d-flex flex-column flex-md-row justify-content-between gap-3 align-items-md-start mb-4">
        <div><p className="text-uppercase text-primary fw-semibold small mb-1">Accueil Parent</p><h1 className="h2 mb-1">Bonjour, responsable familial</h1><p className="text-secondary mb-0">Dernière mise à jour fictive : aujourd’hui</p></div>
        <div><label htmlFor="student-example" className="form-label fw-semibold">Enfant consulté</label><select id="student-example" className="form-select" defaultValue="example"><option value="example">Exemple fictif</option></select></div>
      </div>
      <div className="row g-4 mb-4">
        <div className="col-md-6 col-xl-4"><section className="card h-100 border-0 shadow-sm"><div className="card-body p-4"><TrendingUp className="text-primary mb-3" aria-hidden="true" /><h2 className="h5">Progression</h2><p className="text-secondary">Emplacement du futur résumé, sans donnée calculée.</p><span className="badge text-bg-secondary">Indisponible dans le prototype</span></div></section></div>
        <div className="col-md-6 col-xl-4"><section className="card h-100 border-0 shadow-sm"><div className="card-body p-4"><AlertTriangle className="text-warning-emphasis mb-3" aria-hidden="true" /><h2 className="h5">Points d’attention</h2><p className="text-secondary">Aucune difficulté réelle n’est chargée.</p><Link href="/parent/enfants" className="btn btn-outline-primary btn-sm">Voir les enfants</Link></div></section></div>
        <div className="col-md-6 col-xl-4"><section className="card h-100 border-0 shadow-sm"><div className="card-body p-4"><BookOpen className="text-primary mb-3" aria-hidden="true" /><h2 className="h5">Activité recommandée</h2><p className="text-secondary">Les recommandations seront ajoutées avec le moteur métier.</p><Link href="/parent/activites" className="btn btn-primary btn-sm">Voir les activités <ArrowRight size={16} aria-hidden="true" /></Link></div></section></div>
      </div>
      <section className="card border-0 shadow-sm"><div className="card-body p-4"><h2 className="h4">Score académique futur</h2><p className="text-secondary mb-0">Aucun score fictif n’est affiché. Cette zone documente uniquement l’emplacement prévu.</p></div></section>
    </>
  );
}
