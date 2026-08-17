import Link from 'next/link';
import { FileQuestion } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <main className="container py-5 text-center">
      <span className="sc-feature-icon mb-3" aria-hidden="true"><FileQuestion size={26} /></span>
      <h1>Page introuvable</h1>
      <p className="lead text-secondary">
        La page demandée n’existe pas ou ne peut pas être affichée.
      </p>
      <Link href="/" className="btn btn-primary">Retour à l’accueil</Link>
    </main>
  );
}
