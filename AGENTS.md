# MathVision AI repository instructions

## Scope

This repository is a TypeScript/React frontend and a Python/FastAPI backend. Phase 6 is complete: the platform includes mathematical reference content, the first-class Advanced Mathematical Analysis workspace, security headers, responsive/accessibility improvements, operational documentation, and the Phase 1–5 capabilities. Keep future changes consistent with the truthful limitations documented here.

## Architecture boundaries

- `frontend/src/` owns presentation, navigation, theme state, and typed API clients; it must not contain heavy image-processing logic.
- `backend/app/api/` owns HTTP routing and serialization only.
- `backend/app/core/` owns configuration, logging, and cross-cutting concerns.
- `backend/app/db/` and `backend/alembic/` own persistence configuration and migrations.
- Mathematical, imaging, persistence, and model logic belongs in `backend/app/mathematics/`, `backend/app/imaging/`, and `backend/app/services/`, isolated from routes. Feature extraction lives in `backend/app/imaging/features.py`, algorithms in `backend/app/imaging/algorithms.py`, quality metrics in `backend/app/mathematics/metrics.py`, experiment persistence in `backend/app/services/experiment_service.py`, and recommendation training/prediction in `backend/app/services/recommendation_service.py`.
- Keep the root `docker-compose.yml` and Dockerfiles reproducible; use `.env.example` for documented configuration without secrets.

## Conventions

- Use English for identifiers, comments, routes, and first-version UI copy.
- Prefer small, typed modules and explicit return types for public functions.
- Do not use `any` in TypeScript or fabricate metrics, model outputs, or confidence values.
- Keep design tokens in `frontend/tailwind.config.ts` and reusable styles in `frontend/src/styles/`.
- Keep API responses modeled with Pydantic and frontend DTOs/Zod schemas.

## Required validation

From `mathvision-ai/`:

- Backend: `python -m ruff check backend`, `python -m pytest backend/tests`, `python -m mypy backend/app`.
- Frontend: `pnpm --dir frontend lint`, `pnpm --dir frontend typecheck`, `pnpm --dir frontend test -- --run`, `pnpm --dir frontend build`.
- Infrastructure: `docker compose config` and `docker compose build` when Docker is available.

Run the relevant checks after every phase and fix genuine failures before reporting completion. If a tool is unavailable, record the exact limitation rather than claiming the check passed.

## Testing and security

- Test behavior, not implementation details. Tests must cover upload validation, processing, MSE/RMSE/PSNR/SSIM behavior, comparison/ranking, persistence, duplicate/mismatch protection, exports, model training/status, recommendation limits, security headers, mathematics content, routing, navigation, and theme switching.
- Treat uploads as untrusted: validate size, MIME type, extension, decoding, dimensions, and generated storage names; never trust user paths or retain files indefinitely by default. Source and processed files are temporary; experiment metadata and metric snapshots are durable through PostgreSQL.
- Never commit secrets, generated model artifacts, uploads, database volumes, or build output.

## Documentation

Update `README.md` and the relevant `docs/` page when commands, architecture, environment variables, or phase scope changes. Keep documentation truthful about what is implemented.

## Important locations

- Plan: `IMPLEMENTATION_PLAN.md`
- Frontend entry: `frontend/src/main.tsx`
- Frontend shell: `frontend/src/components/layout/`
- Backend entry: `backend/app/main.py`
- Health route: `backend/app/api/routes/health.py`
- Image and experiment routes: `backend/app/api/routes/images.py`, `backend/app/api/routes/analysis.py`, `backend/app/api/routes/processing.py`, and `backend/app/api/routes/experiments.py`
- Imaging, experiment, and persistence services: `backend/app/services/`, `backend/app/imaging/`, `backend/app/mathematics/`, and `backend/app/db/models/`
- Workspace page: `frontend/src/pages/WorkspacePage.tsx`
- Model Insights page: `frontend/src/pages/ModelInsightsPage.tsx`
- Recommendation API: `backend/app/api/routes/recommendations.py` and `backend/app/services/recommendation_service.py`
- Mathematical analysis API/service: `backend/app/api/routes/mathematical_analysis.py`, `backend/app/services/mathematical_analysis_service.py`, and `backend/app/mathematics/`
- Mathematical analysis UI: `frontend/src/pages/MathematicalAnalysisPage.tsx` and `frontend/src/features/mathematical-analysis/`
- Mathematics page: `frontend/src/pages/MathematicsPage.tsx`
- Deployment guide: `docs/deployment.md`
- Database base and migration environment: `backend/app/db/` and `backend/alembic/`
- CI: `.github/workflows/`
