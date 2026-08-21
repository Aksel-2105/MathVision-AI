# Phase 5 API reference

The backend serves OpenAPI documentation at `/docs` while running. All routes are versioned under `/api/v1`.

## Processing and comparison

Phase 3 health, image, analysis, and processing routes remain available. `POST /api/v1/comparisons` accepts `{ "processing_ids": ["...", "..."] }`, requires at least two results from the same source image, and returns deterministically ranked rows with the ranking policy.

## Experiments

- `POST /api/v1/experiments` creates a persistent experiment from an uploaded image: `{ "image_id": "...", "name": "Denoising sweep", "description": "..." }`.
- `GET /api/v1/experiments` lists saved experiments; `image_id` can filter the list.
- `GET /api/v1/experiments/{experiment_id}` returns metadata and saved run snapshots.
- `POST /api/v1/experiments/{experiment_id}/runs` saves a processing result snapshot by `{ "processing_id": "..." }`.
- `GET /api/v1/experiments/{experiment_id}/comparison` ranks persisted runs.
- `GET /api/v1/experiments/{experiment_id}/export?format=json|csv` exports the experiment and comparison data.
- `DELETE /api/v1/experiments/{experiment_id}` deletes experiment metadata and its run snapshots.

Run snapshots include algorithm, parameters, metric values, output URL, and timestamp. The source and processed image files remain temporary and can expire independently of the persisted experiment record.

## Ranking policy

`score = 0.50*SSIM + 0.35*min(PSNR/50, 1) + 0.15*speed_score`, where `speed_score = max(0, 1 - execution_ms/5000)`. Missing PSNR or SSIM contributes zero for that component. Ties are resolved by SSIM, PSNR, then execution time.

## Recommendations and model training

- `GET /api/v1/recommendations/model` returns whether a model is trained, its version, sample/class counts, validation metadata, feature names, and limitations.
- `POST /api/v1/recommendations/train` builds training rows from experiments with source feature snapshots and saved runs. The best run is selected with the Phase 4 ranking policy, and the model is persisted under `MODEL_DIR`.
- `POST /api/v1/recommendations` accepts `{ "image_id": "..." }` and returns the recommended algorithm, class probabilities, extracted features, global feature importance, explanation, and limitations. It returns `409 recommendation_model_not_trained` until training succeeds.

The model is a class-balanced Random Forest. A stratified 25% holdout is used only when there are at least four samples, two classes, and at least two samples per class; otherwise validation accuracy is explicitly unavailable. This is not a benchmark-grounded classifier and does not claim causal explanations or production-level generalization.
