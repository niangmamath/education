import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

// Font configuration
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

// Metadata for the application
export const metadata: Metadata = {
  title: {
    default: 'StudentConnect - Plateforme EdTech',
    template: '%s | StudentConnect',
  },
  description: 'Plateforme éducative innovante pour les élèves de 6 à 11 ans et leurs parents',
  keywords: ['education', 'edtech', 'élèves', 'parents', 'score académique', 'remédiation'],
  authors: [{ name: 'tidianesarrndiaye-org' }],
  openGraph: {
    type: 'website',
    locale: 'fr_FR',
    url: 'https://studentconnect.example.com',
    siteName: 'StudentConnect',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative innovante pour les élèves de 6 à 11 ans et leurs parents',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative innovante pour les élèves de 6 à 11 ans et leurs parents',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: '#ffffff',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

// Root Layout component
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.className} ${inter.variable}`}>
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  );
}
