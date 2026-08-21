# Architecture

Phase 6 uses the two-application monorepo established in Phase 1:

```text
Browser
  │
  ├── frontend (React/Vite static app)
  │       │ typed API calls
  │       ▼
  └── backend (FastAPI /api/v1)
          │ typed service and domain modules
          ▼
      PostgreSQL via SQLAlchemy/Alembic
```

The frontend shell is responsible for navigation, responsive layout, theme preference, upload validation, preview, analysis presentation, processing controls, comparison, and history presentation. The backend exposes versioned health, image upload/metadata/content/delete, analysis, algorithm-list, processing, comparison, experiment history, and export contracts. Source bytes live under `data/runtime/uploads` and generated PNG outputs under `data/runtime/processed`; these remain temporary. Experiment metadata, processing parameters, and metric snapshots persist in PostgreSQL through SQLAlchemy/Alembic.

Image features are computed from decoded pixels in `backend/app/imaging/features.py`. The noise indicator is a labeled no-reference heuristic. Algorithms are isolated in `backend/app/imaging/algorithms.py`, quality measures in `backend/app/mathematics/metrics.py`, and experiment persistence/ranking/export logic in `backend/app/services/experiment_service.py`. PSNR and SSIM are calculated against the uploaded source. Ranking is deliberately documented and deterministic.

Phase 5 stores the source feature snapshot on each experiment. `backend/app/services/recommendation_service.py` turns experiments with saved runs into training rows, labels each row with the highest-ranked algorithm, and persists a versioned Random Forest artifact under `MODEL_DIR`. The recommendation route extracts a fresh feature vector from the uploaded image and returns probabilities, global feature importance, an explanation based on the most influential features, and explicit dataset limitations. Model artifacts are runtime data and must not be committed.

The frontend serves a static SPA through Nginx in production. Nginx adds browser security headers, while FastAPI adds equivalent API headers and disables API caching. Uploads and processed outputs are temporary runtime files; PostgreSQL stores experiment metadata and metric snapshots; model artifacts are local runtime files under `MODEL_DIR` and should be backed up or retrained only from trusted experiment data.
