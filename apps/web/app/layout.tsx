import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: {
    default: 'StudentConnect - Plateforme EdTech',
    template: '%s | StudentConnect',
  },
  description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  keywords: ['education', 'edtech', 'élèves', 'parents', 'remédiation'],
  authors: [{ name: 'tidianesarrndiaye-org' }],
  openGraph: {
    type: 'website',
    locale: 'fr_FR',
    url: 'https://studentconnect.example.com',
    siteName: 'StudentConnect',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'StudentConnect - Plateforme EdTech',
    description: 'Plateforme éducative pour les élèves de 6 à 11 ans et leurs parents',
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: '#2457c5',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr" data-scroll-behavior="smooth">
      <body className={`${inter.className} ${inter.variable}`}>{children}</body>
    </html>
  );
}
