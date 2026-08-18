import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ParentSignUpForm } from '../../components/auth/parent-sign-up-form';

export const metadata = {
  title: 'Créer un compte Parent',
  description: 'Ouvrir un compte Parent et recevoir son code de famille',
};

export default function InscriptionParentPage() {
  return (
    <main className="container py-5">
      <Link href="/" className="sc-lien-retour mb-5">
        <ArrowLeft size={18} aria-hidden="true" />
        Retour à l’accueil
      </Link>

      <div className="row g-5 justify-content-center align-items-start">
        <div className="col-lg-5 col-xl-4">
          <p className="sc-oeilleton sc-oeilleton-indigo">Inscription</p>
          <h1 className="mb-3">Ouvrir un compte parent</h1>
          <p className="text-secondary">
            Le compte parent est le premier : c’est lui qui reçoit le code de la
            famille, et c’est ce code qui rattache les profils de vos enfants.
          </p>
          <p className="sc-marge mb-0 text-secondary">
            Un profil enfant ne demande ni adresse e-mail ni téléphone. Vous
            pouvez le créer vous-même, ou laisser votre enfant le faire avec le
            code de la famille — vous l’acceptez ensuite.
          </p>
        </div>

        <div className="col-lg-6 col-xl-5">
          <div className="sc-feuille-auth">
            <ParentSignUpForm />
          </div>

          <p className="mt-4 mb-0 text-secondary">
            Vous avez déjà un compte ? <Link href="/connexion">Se connecter</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
