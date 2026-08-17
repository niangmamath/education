/**
 * Configuration du web StudentConnect.
 *
 * @type {import('next').NextConfig}
 */

/**
 * Les hôtes publics d'où les actions serveur sont acceptées.
 *
 * Next vérifie que l'en-tête `Origin` d'une action serveur correspond à l'hôte
 * qui a rendu la page, et refuse sinon : c'est sa protection contre le CSRF, et
 * elle est utile. Derrière un tunnel — ngrok pour montrer le site à quelqu'un —
 * le navigateur envoie l'hôte public tandis que Next voit le sien, les deux ne
 * correspondent pas, et **toute connexion échoue** : se connecter est une action
 * serveur.
 *
 * `PUBLIC_HOST` déclare cet hôte, sans protocole ni barre finale. Rien n'est
 * ouvert par défaut : sans la variable, la liste est vide et le comportement
 * d'origine tient.
 */
const publicHosts = (process.env.PUBLIC_HOST ?? '')
  .split(',')
  .map((host) => host.trim().replace(/^https?:\/\//, '').replace(/\/$/, ''))
  .filter(Boolean);

const nextConfig = {
  output: 'standalone',

  typescript: {
    // Le typage est tenu par tsconfig.json et par `pnpm lint`.
    ignoreBuildErrors: false,
  },

  images: {
    unoptimized: true,
  },

  // En développement, Next refuse aussi les requêtes de développement venues
  // d'une autre origine ; le tunnel en est une.
  allowedDevOrigins: publicHosts,

  experimental: {
    serverActions: {
      allowedOrigins: publicHosts,
    },
  },
};

export default nextConfig;
