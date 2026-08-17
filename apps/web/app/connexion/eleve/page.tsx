import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ChildLoginForm } from '../../../components/auth/child-login-form';

export const metadata = {
  title: 'Connexion Élève',
  description: 'Entrer dans l’espace Élève avec le code de sa famille',
};

/**
 * La page de l'enfant, et on lui parle à elle : « tu », phrases courtes, aucun
 * mot d'adulte. C'est aussi la page où l'inscription d'un enfant renvoie, donc
 * c'est ici que se lit `demande`.
 */
export default async function ConnexionElevePage({
  searchParams,
}: {
  searchParams: Promise<{ demande?: string }>;
}) {
  const { demande } = await searchParams;

  return (
    <main className="sc-student-page container py-5">
      <Link href="/" className="d-inline-flex align-items-center gap-2 mb-5">
        <ArrowLeft size={18} aria-hidden="true" />
        Retour à l’accueil
      </Link>

      <div className="row g-5 justify-content-center align-items-start">
        <div className="col-lg-5 col-xl-4">
          <p className="sc-oeilleton">Connexion</p>
          <h1 className="mb-3">Bonjour !</h1>
          <p className="text-secondary">
            Il te faut ton pseudo et le code de ta famille. Si tu ne connais pas
            le code, demande-le à un adulte de chez toi.
          </p>
          <p className="sc-marge sc-marge-seyes mb-0 text-secondary">
            Vous êtes un parent ? <Link href="/connexion">Votre espace est ici.</Link>
          </p>
        </div>

        <div className="col-lg-6 col-xl-5">
          {demande ? (
            <div className="alert alert-info" role="status">
              <strong>Ton profil est enregistré.</strong> Un adulte de ta famille
              doit l’accepter avant que tu puisses entrer. Reviens ici après.
            </div>
          ) : null}

          <div className="sc-feuille-auth">
            <ChildLoginForm />
          </div>

          <p className="mt-4 mb-0 text-secondary">
            Tu n’as pas encore de profil ?{' '}
            <Link href="/inscription/eleve">En créer un</Link>
          </p>
        </div>
      </div>
    </main>
  );
}
