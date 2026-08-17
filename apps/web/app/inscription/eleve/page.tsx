import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ChildSignUpForm } from '../../../components/auth/child-sign-up-form';

export const metadata = {
  title: 'Rejoindre sa famille',
  description: 'Créer un profil Élève avec le code de sa famille',
};

export default function InscriptionElevePage() {
  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '34rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <div className="card border-0 shadow-sm">
          <div className="card-body p-4 p-lg-5">
            <ChildSignUpForm />
          </div>
        </div>

        <div className="d-flex flex-column gap-2 mt-4">
          <p className="mb-0">Vous êtes un parent ? <Link href="/inscription">Ouvrir un compte</Link></p>
          <p className="mb-0">Tu as déjà un profil ? <Link href="/connexion/eleve">Entrer</Link></p>
        </div>
      </div>
    </main>
  );
}
