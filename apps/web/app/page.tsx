'use client';

import Link from 'next/link';
import { ArrowRight, BookOpen, BarChart3, Users, Rocket } from 'lucide-react';

export default function ConstructionPage() {
  const features = [
    {
      icon: BookOpen,
      title: 'Arbre de compétences',
      description: 'Modélisation complète des prérequis et dépendances entre compétences',
      status: 'En développement',
    },
    {
      icon: BarChart3,
      title: 'Score de santé académique',
      description: 'Indicateur explicable basé sur les résultats et l\'engagement',
      status: 'En développement',
    },
    {
      icon: Users,
      title: 'Dashboards distincts',
      description: 'Espace Parent avec score et espace Élève gamifié',
      status: 'En développement',
    },
    {
      icon: Rocket,
      title: 'Quick Repairs',
      description: 'Exercices courts (3-7 min) ciblant les lacunes détectées',
      status: 'En développement',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">SC</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">StudentConnect</h1>
                <p className="text-sm text-gray-500">Plateforme EdTech</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full font-medium">
                En développement
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
            Bienvenue sur StudentConnect
          </h1>
          <p className="text-lg text-gray-600 mb-2">
            Plateforme éducative innovante pour les élèves de 6 à 11 ans
          </p>
          <p className="text-lg text-gray-600 mb-6">
            et leurs parents
          </p>
          <p className="text-sm text-gray-500 mb-8">
            Site en construction - Version MVP V0.1
          </p>
          <Link
            href="/health"
            className="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200 font-medium"
          >
            Vérifier l\'état
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card group hover:shadow-lg transition-shadow duration-200"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <feature.icon className="w-5 h-5 text-primary-600" />
                </div>
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                  {feature.status}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Progress Section */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Progression du projet</h2>
            <span className="text-sm text-gray-500">Phase 0</span>
          </div>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Monorepo initialisé</span>
                <span className="text-sm text-green-600 font-medium">100%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full w-full"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">Next.js Frontend</span>
                <span className="text-sm text-blue-600 font-medium">En cours</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full w-1/2"></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">FastAPI Backend</span>
                <span className="text-sm text-gray-500 font-medium">À faire</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-gray-400 h-2 rounded-full w-0"></div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <p className="text-sm text-gray-500">
              © 2026 StudentConnect. Tous droits réservés.
            </p>
            <p className="text-sm text-gray-500 mt-2 sm:mt-0">
              Développé avec Next.js 16, Tailwind CSS 4, et FastAPI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
