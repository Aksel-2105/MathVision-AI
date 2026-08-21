# MathVision AI

**Intelligent Image Analysis, Denoising, Compression, and Mathematical Explanation Platform**

MathVision AI is a scientific image-processing platform built as a React/FastAPI monorepo. The current delivery is **Phase 6 — Mathematics, Hardening, and Final Polish**: it includes the complete image workflow, explainable recommendations, a first-class Advanced Mathematical Analysis workspace, an interactive mathematical reference, security headers, responsive/accessibility improvements, and deployment documentation.

## Phase 6 features

- Responsive React + TypeScript + Vite application shell.
- Desktop sidebar with collapsible and mobile drawer behavior.
- Light/dark theme with persisted preference and reduced-motion-aware styles.
- Honest page states for capabilities scheduled for later phases.
- FastAPI `/api/v1/health` endpoint with OpenAPI documentation.
- Secure image upload with size, extension, MIME, decoder, and dimension validation.
- Temporary UUID-based storage with SHA-256 content hashes and expiry metadata.
- Real image metadata, statistical features, heuristic no-reference noise estimate, and histograms.
- Workspace preview, loading/error states, metric cards, and accessible histogram chart.
- Validated denoising, enhancement, DCT, wavelet, and SVD processing operations.
- MSE, RMSE, PSNR, SSIM, execution time, output size, compression ratio, and coefficient-retention metrics.
- Temporary processed PNG outputs with download links and original/processed previews.
- Persistent experiment and processing-run snapshots through SQLAlchemy/Alembic.
- Transparent comparison ranking based on SSIM, PSNR, and execution speed.
- Experiment history with deletion and JSON/CSV exports.
- Source-image feature snapshots persisted with experiments for reproducible training.
- Random Forest model training from saved experiment outcomes with dataset-aware validation.
- Model status and recommendation APIs with probabilities, feature importance, explanations, and limitations.
- Model Insights training screen and Workspace recommendation control.
- Interactive KaTeX reference for transforms, metrics, notation, and numerical examples.
- About page documenting delivery history, operational boundaries, and engineering commitments.
- API and Nginx security headers, reduced-motion support, mobile focus hygiene, and disabled-state feedback.
- SQLAlchemy/Alembic PostgreSQL foundation.
- Docker Compose services for frontend, backend, and PostgreSQL.
- Backend and frontend CI workflows.

## Advanced Mathematical Analysis

After an image upload, the Workspace exposes four separate primary actions: Quick Analysis, Advanced Mathematical Analysis, AI Diagnosis, and Process Image. Advanced Mathematical Analysis opens the dedicated route `/workspace/images/{imageId}/mathematical-analysis` with fourteen tabs covering matrix/tensor representation, descriptive statistics, probability, histograms, gradients, FFT/DCT, wavelets, SVD, color mathematics, texture, noise, local maps, compression potential, and a structured mathematical report.

The backend endpoint is `POST /api/v1/mathematical-analysis/{image_id}` with a matching retrieval endpoint and JSON/CSV report exports. All supported measurements are computed from the uploaded pixels, and the response includes the method, formula, interpretation, and limitations alongside numerical values. Expensive visualizations use bounded previews while the UI labels the representation used for each result. Local mathematical maps can be recomputed on a 4×4, 8×8, or 16×16 grid.

## Repository layout

```text
mathvision-ai/
├── frontend/       # React, TypeScript, Vite, Tailwind UI
├── backend/        # FastAPI, SQLAlchemy, Alembic
├── docs/           # Architecture and phase documentation
├── .github/        # CI workflows
├── docker-compose.yml
├── AGENTS.md
└── IMPLEMENTATION_PLAN.md
```

## Local setup

1. Copy `.env.example` to `.env` and adjust values if needed.
2. Install backend dependencies with `python -m pip install -e backend[dev]`.
3. Install frontend dependencies with `pnpm --dir frontend install`.
4. In a terminal, enter `backend/`, run `alembic upgrade head`, then run `python -m uvicorn app.main:app --reload`.
5. In a second terminal at the repository root, run `pnpm --dir frontend dev`.

The frontend is available at `http://localhost:5173` and the API at `http://localhost:8000`. The health contract is `http://localhost:8000/api/v1/health`.

## Docker setup

```text
docker compose up --build
```

This starts `frontend`, `backend`, and `db`; the backend applies all Alembic migrations automatically before serving requests. Docker is optional for local UI work but is the intended reproducible environment.

## Publish a direct browser link

The current React interface can be published without redesigning it or asking visitors to install Docker. `Dockerfile.production` packages the built React SPA together with FastAPI, and `render.yaml` describes one public web service plus PostgreSQL.

1. Push the repository to GitHub.
2. In Render, select **New → Blueprint**, choose the repository, and apply `render.yaml`.
3. After the build completes, open the generated `https://...onrender.com` URL.

The public URL serves both the interface and the API on the same origin. This removes the need to manually set a frontend API URL in production while preserving the existing UI and routes. Local Docker Compose remains available for development.

## Validation commands

```text
python -m ruff check backend
python -m pytest backend/tests
python -m mypy backend/app
pnpm --dir frontend lint
pnpm --dir frontend typecheck
pnpm --dir frontend test -- --run
pnpm --dir frontend build
docker compose config
docker compose build
```

## Environment variables

See `.env.example`. No secrets belong in the repository. `DATABASE_URL` points to PostgreSQL in Docker. Source images and processed outputs remain temporary; experiment metadata and metric snapshots are persisted.

## Roadmap

Phase 6 and the Advanced Mathematical Analysis feature are complete. See `docs/deployment.md`, `docs/architecture.md`, and `IMPLEMENTATION_PLAN.md` for operational and design boundaries.

## License

MIT. See `LICENSE`.
