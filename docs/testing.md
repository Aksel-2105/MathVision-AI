# Testing strategy

Phase 6 keeps tests close to the foundations and real image data flow:

- Backend tests assert the versioned health response through FastAPI's test client.
- Backend tests cover valid PNG upload, metadata/content retrieval, malformed and mismatched uploads, feature extraction, histogram shape, entropy, and analysis responses.
- Backend tests cover parameter bounds, algorithm-list responses, denoising/enhancement/compression outputs, full-reference metrics, small-image SSIM notes, and processed-content retrieval.
- Backend tests cover SQLite-backed experiment creation, run snapshots, ranking, duplicate protection, source-image mismatch protection, deletion, and JSON/CSV exports.
- Backend tests cover recommendation training from saved experiment outcomes, model status persistence, insufficient training data, untrained recommendations, probabilities, feature importance, and truthful limitations.
- Frontend tests assert the application shell, route navigation, and persisted theme switching.
- Frontend tests cover the Workspace scope, upload validation, and API-facing rendering boundaries.
- Frontend tests cover saved comparison ranking presentation and the active history/comparison routes.
- Frontend tests cover the Model Insights training flow and metadata/limitation presentation.
- Frontend tests cover the Mathematics page content, KaTeX-backed equation rendering, and final Home copy.
- Backend tests verify API security headers. Nginx headers are syntax-reviewed in the production configuration.
- Ruff, mypy, TypeScript, ESLint, Vitest, and the Vite production build are part of the local validation contract.
- Docker Compose configuration and image builds are validated when Docker is available.

No test should accept fabricated metrics or model outputs. Docker image execution remains dependent on a locally installed Docker runtime.
