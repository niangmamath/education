import Link from 'next/link';
import { ArrowRight, BookOpen, Clock3, Star } from 'lucide-react';
import { PrototypeNotice } from '../../components/ui/prototype-notice';

export const metadata = { title: 'Espace Élève' };

export default function EleveHomePage() {
  return (
    <>
      <PrototypeNotice />
      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Accueil Élève</p>
        <h1 className="h2 mb-2">Bonjour, élève exemple</h1>
        <p className="text-secondary mb-0">Choisis une petite étape pour commencer.</p>
      </header>

      <section className="card border-0 shadow-sm sc-student-hero mb-4">
        <div className="card-body p-4 p-lg-5">
          <div className="row align-items-center g-4">
            <div className="col-lg-8">
              <span className="badge rounded-pill text-bg-primary mb-3">Objectif fictif du moment</span>
              <h2 className="h3">Découvrir une activité courte</h2>
              <p className="text-secondary mb-3">
                Aucune activité réelle n’est encore recommandée. Cette carte montre seulement la future action principale.
              </p>
              <div className="d-flex align-items-center gap-2 small text-secondary mb-4">
                <Clock3 size={18} aria-hidden="true" />
                <span>Durée indicative fictive : 5 minutes</span>
              </div>
              <Link href="/eleve/activites" className="btn btn-primary btn-lg">
                Voir les activités <ArrowRight size={19} aria-hidden="true" />
              </Link>
            </div>
            <div className="col-lg-4 text-center">
              <span className="sc-student-illustration" aria-hidden="true"><BookOpen size={56} /></span>
            </div>
          </div>
        </div>
      </section>

      <div className="row g-4">
        <div className="col-12 col-md-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <h2 className="h5">Ma progression</h2>
              <p className="text-secondary">Aucune progression réelle n’est calculée dans le prototype.</p>
              <Link href="/eleve/progression" className="btn btn-outline-primary">Voir l’état prototype</Link>
            </div>
          </section>
        </div>
        <div className="col-12 col-md-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <Star className="text-warning-emphasis mb-3" aria-hidden="true" />
              <h2 className="h5">Mes récompenses</h2>
              <p className="text-secondary">Aucun point, classement ou récompense réelle n’est attribué.</p>
              <Link href="/eleve/recompenses" className="btn btn-outline-primary">Comprendre le futur espace</Link>
            </div>
          </section>
        </div>
      </div>
    </>
  );
}
