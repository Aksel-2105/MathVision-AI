# MathVision AI implementation plan

## Delivery rule

Work proceeds phase by phase. Phases 1–5 are complete and this delivery completes Phase 6.

## Architecture

```text
React + TypeScript + Vite + Tailwind
          │ typed HTTP boundary (future feature APIs)
          ▼
FastAPI + Pydantic
          │ service/domain boundary
          ├── core configuration and logging
          └── SQLAlchemy/Alembic → PostgreSQL
```

The frontend owns the responsive application shell, navigation, theme preference, typed API calls, processing presentation, comparison, and history. The backend owns the versioned API, configuration, SQLAlchemy models, and migrations. Algorithms, metrics, and experiment services remain outside routes so HTTP handlers stay thin.

## Phase 1 — Foundation (complete)

1. Preserve the existing workspace by creating an isolated `mathvision-ai/` monorepo.
2. Add repository guidance, environment templates, ignore rules, editor settings, license, README, and this plan.
3. Scaffold the frontend with React, TypeScript, Vite, Tailwind, React Router, TanStack Query, Vitest, and React Testing Library.
4. Build a responsive application shell with a collapsible desktop sidebar, mobile drawer, top bar, accessible navigation, design tokens, and light/dark theme persistence.
5. Scaffold the backend with FastAPI, Pydantic settings, structured logging, SQLAlchemy, and Alembic.
6. Add the versioned `GET /api/v1/health` endpoint with a typed response and a minimal foundation database migration.
7. Add Docker Compose services for frontend, backend, and PostgreSQL, plus Dockerfiles and health checks.
8. Add backend/frontend CI workflows that invoke commands present in the repository.
9. Add Phase 1 tests for the health response, route rendering, navigation, and theme switching.
10. Run tests, linting, type checks, production builds, and Docker validation; fix failures or document unavailable external tooling.

## Phase 3 — Processing and quality metrics (complete)

1. Add a typed registry for denoising, enhancement, and mathematical compression algorithms with bounded parameters.
2. Implement denoising, enhancement, and DCT/wavelet/SVD compression operations.
3. Add MSE, RMSE, PSNR, SSIM, execution-time, output-size, compression-ratio, and coefficient-retention metrics.
4. Add temporary processed-output storage and processing metadata/content endpoints.
5. Add a Workspace algorithm selector, parameter controls, output previews, download link, and metrics presentation.
6. Add backend unit/integration tests and frontend behavior tests for processing.

## Phase 4 — Comparison, experiments, and exports (this delivery)

1. Add persistent `experiments` and `experiment_runs` tables with an Alembic migration.
2. Save processing metric snapshots and parameters while keeping image outputs temporary.
3. Compare multiple processing results from one source image and rank them using a documented SSIM/PSNR/speed policy.
4. Add experiment history, duplicate/mismatch protection, deletion, and JSON/CSV exports.
5. Replace Compare and Experiments placeholders with functional frontend pages and Workspace save controls.
6. Add backend persistence/comparison/export tests and frontend comparison coverage.

## Phase 5 — Explainable recommendation and model training (this delivery)

1. Persist source-image feature snapshots with experiments and add the model artifact configuration/migration.
2. Build a reproducible training dataset from saved experiment outcomes, selecting each experiment's best run with the Phase 4 ranking policy.
3. Train and persist a class-balanced Random Forest with honest holdout validation only when the dataset supports it.
4. Add model-status, training, and recommendation endpoints with feature vectors, probabilities, feature importance, explanations, and limitations.
5. Replace the Model Insights placeholder and add a Workspace recommendation control connected to the trained model.
6. Add backend and frontend coverage for training, model metadata, insufficient data, untrained recommendations, and truthful limitations.

## Phase 6 — Mathematics, hardening, and final polish (complete)

1. Replace Mathematics and About placeholders with an accessible mathematical reference and project/limitations reference.
2. Render DWT, DCT, FFT, SVD, MSE, PSNR, SSIM, Entropy, and the project score objective with definitions, symbols, and numerical examples.
3. Add security response headers to FastAPI and the production Nginx server, preserve bounded upload validation, and prevent hidden mobile navigation controls from remaining focusable.
4. Improve responsive and reduced-motion behavior, disabled control feedback, truthful Home copy, and final navigation states.
5. Add deployment, configuration, validation, retention, and operational limitation documentation.
6. Add Phase 6 tests and run the complete backend/frontend/infrastructure validation suite.

## Definition of done for Phase 1

- The frontend has a production build and passing tests/type checks/lint.
- The backend imports, the health tests pass, and lint/type checks pass where installed.
- Alembic and Docker Compose configuration are syntactically coherent.
- The app clearly labels future capabilities as deferred rather than presenting fabricated results.
- Documentation and CI commands match the actual files.

## Phase 2 — Upload and analysis (complete)

1. Add secure upload limits, extension/MIME/decoder validation, decompression-bomb protection, UUID storage names, SHA-256 hashes, and temporary retention.
2. Add versioned image upload, metadata, content, delete, and analysis endpoints under `/api/v1`.
3. Extract dimensions, channels, color mode, file size, intensity statistics, entropy, contrast, edge density, Laplacian variance, brightness, saturation, gradient statistics, and high-frequency energy from real image pixels.
4. Return a truthful no-reference noise estimate with its heuristic method and limitations; do not present it as a trained classifier.
5. Implement the Workspace upload flow with client/server validation, preview, temporary retention messaging, loading/error states, metric cards, and an accessible SVG histogram.
6. Add backend integration/unit coverage and frontend behavior coverage for upload, analysis, validation, and rendering.

## Phase 2 definition of done

- Valid supported images can be uploaded, decoded, stored with a generated identifier, previewed, and analyzed.
- Invalid, oversized, malformed, mismatched, or unsafe uploads receive structured errors.
- Analysis values are computed from actual image data and exposed with explicit definitions and limitations.
- Histograms and metric cards render the API response without fabricated values.
- Processing and recommendation controls were intentionally deferred at the Phase 2 boundary and are implemented in later completed phases.

## Phase 3 definition of done

- Supported algorithms execute from validated parameters and return real encoded output images.
- Full-reference quality metrics are computed against the uploaded source and expose limitations when PSNR or SSIM is undefined.
- Processed results are temporary, retrievable, downloadable, and covered by API tests.
- The Workspace can configure, run, preview, and measure one processing result at a time.
- Comparison, history, durable persistence, and exports were intentionally deferred at the Phase 3 boundary and are implemented in later completed phases.

## Phase 4 definition of done

- Experiments and processing-run snapshots persist through SQLAlchemy/PostgreSQL and are migrated by Alembic.
- Results from one source image can be compared and ranked with an explicit reproducible policy.
- Experiment history supports retrieval, deletion, and JSON/CSV exports.
- The Workspace can save multiple processing runs, and Compare/Experiments pages are functional.
- Recommendation and model training were intentionally deferred at the Phase 4 boundary and are implemented in Phase 5; SHAP is outside the delivered scope.

## Phase 5 definition of done

- Experiments store real source-image feature snapshots through the `0003_source_features` migration.
- Training uses saved experiment outcomes, persists a versioned Random Forest artifact, and reports validation method and dataset limitations.
- Recommendations use real extracted features and return probabilities, feature importance, an explanation, and limitations; an untrained model returns a structured conflict.
- Model Insights and Workspace expose training/recommendation behavior without fabricated metrics.
- Backend/frontend tests, lint, type checks, and production builds pass before the Phase 6 hardening work.

## Phase 6 definition of done

- Mathematics and About routes are functional and explain implemented behavior without fabricated values.
- Security headers, temporary-data boundaries, responsive layout, focus behavior, and reduced-motion handling are documented and tested where practical.
- Local and Docker deployment instructions, configuration, migrations, retention, and validation commands are documented.
- Backend/frontend tests, lint, type checks, production builds, and migration/YAML validation pass; Docker execution is reported separately if the runtime is unavailable.

## Advanced Mathematical Analysis — complete

1. Added isolated backend mathematics modules for descriptive statistics, empirical probability, information theory, gradients, FFT/DCT, wavelets, SVD, texture, noise, local maps, and normalized compression-potential scoring.
2. Added `MathematicalAnalysisService` with reusable real-image intermediates, safe preview bounds, process-local caching, structured report generation, and JSON/CSV export support.
3. Added typed API endpoints under `/api/v1/mathematical-analysis/` and a dedicated frontend route with fourteen mathematical-analysis tabs.
4. Added the four distinct post-upload actions in Workspace, with Advanced Mathematical Analysis using the scientific cyan accent and mathematical icon.
5. Added formula explanations, methods, interpretations, limitations, charts, heatmaps, matrix inspection, report downloads, backend unit coverage, and frontend route coverage.
6. Verified the feature against a real uploaded PNG through the Dockerized API: upload succeeded, analysis completed with fourteen sections, and JSON/CSV exports returned HTTP 200.
