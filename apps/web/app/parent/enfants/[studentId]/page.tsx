import Link from 'next/link';
import { notFound } from 'next/navigation';
import { PrototypeNotice } from '../../../../components/ui/prototype-notice';

type PageProps = {
  params: Promise<{ studentId: string }>;
};

const allowedExampleId = 'eleve-exemple-01';

export function generateStaticParams() {
  return [{ studentId: allowedExampleId }];
}

export const metadata = { title: 'Détail enfant' };

export default async function ParentStudentDetailPage({ params }: PageProps) {
  const { studentId } = await params;

  if (studentId !== allowedExampleId) {
    notFound();
  }

  return (
    <>
      <PrototypeNotice />
      <nav aria-label="Fil d’Ariane" className="mb-3">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link href="/parent">Accueil</Link></li>
          <li className="breadcrumb-item"><Link href="/parent/enfants">Enfants</Link></li>
          <li className="breadcrumb-item active" aria-current="page">Élève exemple</li>
        </ol>
      </nav>

      <header className="mb-4">
        <p className="text-uppercase text-primary fw-semibold small mb-1">Identifiant fictif et opaque</p>
        <h1 className="h2 mb-2">Élève exemple</h1>
        <p className="text-secondary mb-0">
          Aucun résultat scolaire réel n’est associé à ce prototype.
        </p>
      </header>

      <div className="row g-4">
        <div className="col-12 col-lg-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <h2 className="h5">Progression</h2>
              <p className="text-secondary mb-0">Indisponible tant que les données métier ne sont pas implémentées.</p>
            </div>
          </section>
        </div>
        <div className="col-12 col-lg-6">
          <section className="card h-100 border-0 shadow-sm">
            <div className="card-body p-4">
              <h2 className="h5">Compétences et points d’attention</h2>
              <p className="text-secondary mb-0">Aucune compétence ou difficulté fictive n’est présentée comme calculée.</p>
            </div>
          </section>
        </div>
      </div>

      <section className="card border-0 shadow-sm mt-4">
        <div className="card-body p-4">
          <h2 className="h5">Score académique futur</h2>
          <p className="text-secondary mb-0">Aucun score fictif n’est affiché.</p>
        </div>
      </section>
    </>
  );
}
