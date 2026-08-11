# Planning simple

| ID | Travail | Dependances | Statut | Preuve attendue |
|---|---|---|---|---|
| P0-01 | Verifier depot vide | Aucune | Termine | Rapport 01 |
| P0-02 | Fichiers racine | P0-01 | Termine | Rapport 01 |
| P0-03 | ADR initiaux | P0-02 | Termine | ADR |
| P0-04 | Monorepo | P0-03 | Termine | Rapport 02 |
| S1-01 | Next.js et Tailwind | P0-03 | Termine sous reserve lint | Build et typecheck |
| S1-02 | FastAPI | P0-03 | Termine sous reserve CORS | Tests health |
| P0-05A | Docker Compose | P0-04,S1-02 | A faire | Services healthy |
| S1-03 | SQLAlchemy et Alembic | S1-02,P0-05A | A faire | upgrade/downgrade |
| S1-07 | CI | S1-01,S1-02,S1-03 | A faire | Workflows verts |
| P0-05 | Cloturer infrastructure locale | P0-05A,S1-03,S1-07 | A faire | Rapport, commit, push |
| P0-06 | Spike H5P | P0-05 | A faire | Lecture + xAPI |
