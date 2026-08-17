import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ChildSignUpForm } from '../../../components/auth/child-sign-up-form';

export const metadata = {
  title: 'Rejoindre sa famille',
  description: 'Créer un profil Élève avec le code de sa famille',
};

export default function InscriptionElevePage() {
  return (
    <main className="sc-student-page container py-5">
      <Link href="/" className="d-inline-flex align-items-center gap-2 mb-5">
        <ArrowLeft size={18} aria-hidden="true" />
        Retour à l’accueil
      </Link>

      <div className="row g-5 justify-content-center align-items-start">
        <div className="col-lg-5 col-xl-4">
          <p className="sc-oeilleton">Inscription</p>
          <h1 className="mb-3">Rejoindre ta famille</h1>
          <p className="text-secondary">
            Choisis un pseudo et un code secret à six chiffres. Tu auras aussi
            besoin du code de ta famille : demande-le à un adulte de chez toi.
          </p>
          <p className="sc-marge sc-marge-seyes mb-0 text-secondary">
            Quand tu auras fini, un adulte devra accepter ton profil avant que tu
            puisses entrer.
          </p>
        </div>

        <div className="col-lg-6 col-xl-5">
          <div className="sc-feuille-auth">
            <ChildSignUpForm />
          </div>

          <p className="mt-4 mb-0 text-secondary">
            Tu as déjà un profil ? <Link href="/connexion/eleve">Entrer</Link>
            <br />
            Vous êtes un parent ? <Link href="/inscription">Ouvrir un compte</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
