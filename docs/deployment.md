# Deployment and operations

## Local development

1. Copy `.env.example` to `.env` and set a non-default PostgreSQL password for shared environments.
2. Install backend dependencies with `python -m pip install -e backend[dev]`.
3. Install frontend dependencies with `pnpm --dir frontend install`.
4. Start PostgreSQL. In a terminal, enter `backend/`, run `alembic upgrade head`, then run `python -m uvicorn app.main:app --reload`. The settings loader accepts `.env` from either the current directory or the repository root.
5. In a second terminal at the repository root, run `pnpm --dir frontend dev`.

The API is available at `http://localhost:8000`, the SPA at `http://localhost:5173`, and OpenAPI documentation at `http://localhost:8000/docs`.

## Advanced Mathematical Analysis

The uploaded-image Workspace provides a dedicated Advanced Mathematical Analysis action. It opens `/workspace/images/{imageId}/mathematical-analysis` and calls the versioned mathematical-analysis API on demand. The analysis is cached for the running backend process and can be exported with:

- `GET /api/v1/mathematical-analysis/{analysis_id}/export?format=json`
- `GET /api/v1/mathematical-analysis/{analysis_id}/export?format=csv`

The feature computes its supported matrix, statistical, probability, histogram, gradient, frequency, wavelet, SVD, texture, noise, local-map, geometry, and compression-potential values from real uploaded pixels. Local maps support 4×4, 8×8, and 16×16 selections; preview maps are bounded for browser safety, while report data remains available through the JSON export.

## Docker Compose

`docker compose up --build` starts PostgreSQL, FastAPI, and the Nginx-served frontend. The backend receives `DATABASE_URL`, `UPLOAD_DIR`, `PROCESSED_DIR`, `MODEL_DIR`, upload limits, and retention settings from Compose. Its entrypoint runs `alembic upgrade head` before starting Uvicorn, so a fresh PostgreSQL volume receives all migrations automatically. Run `docker compose config` before deployment and keep the PostgreSQL volume protected.

## Public browser URL with the current interface

The repository includes `Dockerfile.production` and `render.yaml` for a single-service Render deployment. The compiled React interface and FastAPI API are served from the same public origin, so the existing interface is preserved and visitors do not need Docker or a local API. Render also provisions the PostgreSQL database declared in the Blueprint.

To publish it:

1. Push this repository to GitHub, including `Dockerfile.production` and `render.yaml`.
2. In Render, choose **New → Blueprint**, connect the GitHub repository, and apply the detected `render.yaml`.
3. Wait for the first deployment. Render then provides a URL similar to `https://mathvision-ai.onrender.com`.
4. Open that URL in any browser. The same URL serves the React pages and `/api/v1/*` endpoints.

The service uses the `PORT` supplied by Render, runs database migrations on startup, and exposes `/api/v1/health` as its health check. Uploaded and processed files remain temporary by design; PostgreSQL stores experiment metadata and analysis records. A persistent object-storage strategy should be added before handling important user files at scale.

## Production checklist

- Replace all default database credentials and restrict `CORS_ORIGINS` to the deployed frontend origin.
- Put TLS and an external reverse proxy in front of the services; the included Nginx container serves HTTP for the Compose network boundary.
- For the one-service Render deployment, TLS and the public reverse proxy are provided by Render; do not add a second frontend URL or API URL.
- Confirm the entrypoint migration completed before starting a new backend version; for a manual deployment run `alembic upgrade head` first.
- Persist PostgreSQL backups. Treat `data/runtime/uploads`, `data/runtime/processed`, and `data/runtime/models` as runtime data, not source-controlled assets.
- Monitor disk usage and retention because image files and model artifacts are not automatically uploaded to object storage.
- Retrain the recommendation model after meaningful experiment additions and inspect its limitations; it is not benchmark-grounded.

## Validation

Run backend Ruff, mypy, and pytest; frontend lint, TypeScript, Vitest, and production build; Alembic offline SQL generation; and `docker compose config`/`docker compose build` when Docker is installed. A missing Docker executable is an environment limitation, not a successful Docker validation.
