import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { SignUpForms } from '../../components/auth/sign-up-forms';

export const metadata = {
  title: 'Créer un compte',
  description: 'Ouvrir un compte Parent, ou un profil Élève avec le code de la famille',
};

/**
 * Two ways to open an account, and they are not the same act.
 *
 * A parent opens a family. A child asks to join one she already knows the code
 * of, and waits for an adult — a family code alone must never be enough to join
 * a family, only to ask to. Saying so on the form is what keeps a child from
 * discovering it at her first attempt to sign in.
 */
export default async function InscriptionPage({
  searchParams,
}: {
  searchParams: Promise<{ suite?: string }>;
}) {
  const { suite } = await searchParams;

  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '52rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <h1 className="h2 mb-1">Créer un compte</h1>
        <p className="text-secondary mb-4">
          Un adulte ouvre le compte de la famille. Un enfant n’a besoin ni
          d’adresse e-mail ni de téléphone.
        </p>

        <SignUpForms defaultTab={suite === 'eleve' ? 'eleve' : 'parent'} />

        <p className="mt-4">
          Vous avez déjà un compte ? <Link href="/connexion">Se connecter</Link>
        </p>
      </div>
    </main>
  );
}
