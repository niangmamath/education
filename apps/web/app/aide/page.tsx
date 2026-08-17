import Link from 'next/link';
import { ArrowLeft, CircleHelp } from 'lucide-react';

export const metadata = {
  title: 'Aide',
  description: 'Comment StudentConnect fonctionne, et ce qu’il ne fait pas',
};

/**
 * The questions a family actually asks, answered as the platform actually
 * behaves.
 *
 * The last two are the ones nobody asks and everybody should: what the platform
 * refuses to do is as much a part of the product as what it does, and a family
 * that learns it from an FAQ rather than from a surprise is a family that trusts
 * the rest.
 */
const topics = [
  {
    title: 'À quoi sert StudentConnect ?',
    text: 'À voir où en est un enfant de 6 à 11 ans en français et en mathématiques, et à lui proposer de courtes activités sur ce qui coince. Chaque conclusion affichée porte la règle qui l’a produite et les réponses dont elle vient.',
  },
  {
    title: 'Comment un enfant se connecte-t-il ?',
    text: 'Avec le code de sa famille, son pseudonyme et un code secret de six chiffres. Ni adresse e-mail, ni téléphone : un compte enfant n’en demande jamais. Le code de la famille se trouve dans l’espace Parent, page « Mes enfants ».',
  },
  {
    title: 'Un enfant peut-il créer son profil tout seul ?',
    text: 'Oui, s’il connaît le code de sa famille — mais le profil attend qu’un adulte l’accepte avant de pouvoir entrer. Un code de famille seul ne suffit jamais à rejoindre une famille, seulement à le demander.',
  },
  {
    title: 'Que se passe-t-il la première fois ?',
    text: 'L’enfant passe un court test, « Pour faire connaissance » : une question par compétence, sans minuteur et sans note. Il sert à savoir par où commencer, pas à classer.',
  },
  {
    title: 'Y a-t-il des notes ?',
    text: 'Non, et c’est une règle du produit. Une compétence est lue en trois mots — acquise, en cours d’acquisition, non acquise — accompagnés des réponses comptées. Il existe un score de santé pour le parent, qui résume ces lectures sans jamais en remplacer une, et qui ne compare aucun enfant à un autre.',
  },
  {
    title: 'Que voit l’enfant, que voit le parent ?',
    text: 'L’enfant voit des activités et leur durée, ses résultats et sa progression. Il ne voit ni score, ni difficulté nommée : une liste de réparations remise à un enfant est un jugement auquel il ne peut pas répondre. Le parent voit le diagnostic complet, avec la raison de chaque conclusion.',
  },
  {
    title: 'La plateforme donne-t-elle des activités toute seule ?',
    text: 'Non. Elle propose, et le parent donne — en un clic, sans avoir à ressaisir. La seule exception est le test d’entrée, remis automatiquement à l’activation d’un profil, parce qu’un diagnostic qui attend qu’on y pense n’a pas lieu.',
  },
  {
    title: 'Pourquoi une difficulté n’est-elle parfois pas proposée ?',
    text: 'Parce qu’un prérequis est lui-même en difficulté. Demander d’assurer les additions quand le vrai problème est le comptage fait travailler ce qui bute plutôt que ce qui bloque. La difficulté reste affichée, avec ce qu’elle attend.',
  },
  {
    title: 'Recevrai-je des e-mails ou des alertes ?',
    text: 'Pas aujourd’hui. La page « Ce qui a changé » relit ce que la plateforme sait déjà ; rien n’est envoyé nulle part, et rien n’est marqué comme lu. L’envoi viendra plus tard, et il sera annoncé.',
  },
];

export default function AidePage() {
  return (
    <main className="container py-5">
      <div className="mx-auto" style={{ maxWidth: '52rem' }}>
        <Link href="/" className="d-inline-flex align-items-center gap-2 mb-4">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour à l’accueil
        </Link>

        <header className="mb-4">
          <span className="sc-feature-icon mb-3" aria-hidden="true">
            <CircleHelp size={24} />
          </span>
          <h1>Aide</h1>
          <p className="lead text-secondary">
            Comment la plateforme fonctionne, et ce qu’elle s’interdit de faire.
          </p>
        </header>

        <div className="vstack gap-3">
          {topics.map((topic) => (
            <section className="card border-0 shadow-sm" key={topic.title}>
              <div className="card-body p-4">
                <h2 className="h5">{topic.title}</h2>
                <p className="text-secondary mb-0">{topic.text}</p>
              </div>
            </section>
          ))}
        </div>

        <div className="d-flex flex-wrap gap-3 mt-4">
          <Link href="/inscription" className="btn btn-primary">
            Créer un compte
          </Link>
          <Link href="/connexion" className="btn btn-outline-primary">
            Se connecter
          </Link>
        </div>
      </div>
    </main>
  );
}
