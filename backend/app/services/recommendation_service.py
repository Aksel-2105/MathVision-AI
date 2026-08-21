from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import joblib  # type: ignore[import-untyped]
import numpy as np
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import AppError
from app.db.models.experiments import Experiment
from app.imaging.features import extract_features
from app.imaging.io import load_image_array
from app.schemas.processing import AlgorithmName
from app.schemas.recommendations import (
    ModelStatusResponse,
    RecommendationResponse,
    TrainingResponse,
)
from app.services.image_service import get_validated_image

FEATURE_NAMES: tuple[str, ...] = (
    "width",
    "height",
    "channels",
    "aspect_ratio",
    "mean_intensity",
    "variance",
    "entropy",
    "edge_density",
    "laplacian_variance",
    "brightness",
    "saturation",
    "gradient_mean",
    "gradient_standard_deviation",
    "high_frequency_energy",
)
MODEL_VERSION = "random-forest-v1"


def _numeric_features(source: dict[str, object]) -> list[float]:
    try:
        return [float(cast(Any, source[name])) for name in FEATURE_NAMES]
    except (KeyError, TypeError, ValueError) as error:
        raise AppError(
            "invalid_feature_snapshot",
            "An experiment has an incomplete numeric feature snapshot.",
            422,
        ) from error


def _score(metrics: dict[str, object]) -> float:
    ssim = float(cast(Any, metrics.get("ssim") or 0.0))
    psnr = min(max(float(cast(Any, metrics.get("psnr") or 0.0)) / 50.0, 0.0), 1.0)
    execution = max(
        0.0,
        1.0 - float(cast(Any, metrics.get("execution_time_ms") or 0.0)) / 5000.0,
    )
    return 0.50 * ssim + 0.35 * psnr + 0.15 * execution


def _limitations(metadata: dict[str, object]) -> list[str]:
    limitations = [
        "The model learns from saved experiment outcomes, not a benchmark "
        "ground truth dataset.",
        "A recommendation is only as representative as the experiments used "
        "for training.",
    ]
    if int(cast(Any, metadata.get("class_count", 0))) < 2:
        limitations.append(
            "Only one algorithm class is present; confidence is not comparative."
        )
    if metadata.get("validation_accuracy") is None:
        limitations.append(
            "Validation accuracy is unavailable because the dataset is too "
            "small for a holdout split."
        )
    return limitations


class RecommendationModelStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._bundle: dict[str, object] | None = None

    def clear(self) -> None:
        self._bundle = None
        self.path.unlink(missing_ok=True)

    def _load(self) -> dict[str, object] | None:
        if self._bundle is None and self.path.is_file():
            loaded = joblib.load(self.path)
            if isinstance(loaded, dict):
                self._bundle = loaded
        return self._bundle

    def status(self) -> ModelStatusResponse:
        bundle = self._load()
        if bundle is None:
            return ModelStatusResponse(trained=False)
        metadata = bundle["metadata"]
        if not isinstance(metadata, dict):
            return ModelStatusResponse(trained=False)
        return ModelStatusResponse(
            trained=True,
            model_version=str(metadata["model_version"]),
            trained_at=str(metadata["trained_at"]),
            sample_count=int(metadata["sample_count"]),
            class_count=int(metadata["class_count"]),
            classes=[
                cast(AlgorithmName, str(item))
                for item in cast(list[object], metadata["classes"])
            ],
            validation_accuracy=(
                float(metadata["validation_accuracy"])
                if metadata.get("validation_accuracy") is not None
                else None
            ),
            validation_method=str(metadata["validation_method"]),
            feature_names=[str(item) for item in metadata["feature_names"]],
            limitations=[str(item) for item in metadata["limitations"]],
        )

    def train(self, db: Session) -> TrainingResponse:
        experiments = db.scalars(
            select(Experiment).options(selectinload(Experiment.runs))
        ).all()
        rows: list[list[float]] = []
        labels: list[str] = []
        for experiment in experiments:
            if not experiment.source_features or not experiment.runs:
                continue
            best_run = max(experiment.runs, key=lambda run: _score(run.metrics))
            rows.append(_numeric_features(experiment.source_features))
            labels.append(best_run.algorithm)
        if len(rows) < 2:
            raise AppError(
                "training_insufficient_data",
                "Create at least two saved experiments with processing runs "
                "before training.",
                422,
                {"sample_count": len(rows), "minimum_samples": 2},
            )

        x = np.asarray(rows, dtype=np.float64)
        y = np.asarray(labels)
        classes = sorted(set(labels))
        validation_accuracy: float | None = None
        validation_method = "no_holdout_dataset_too_small"
        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        )
        counts = {label: labels.count(label) for label in classes}
        if len(rows) >= 4 and len(classes) >= 2 and min(counts.values()) >= 2:
            x_train, x_test, y_train, y_test = train_test_split(
                x, y, test_size=0.25, random_state=42, stratify=y
            )
            validation_model = RandomForestClassifier(
                n_estimators=200, random_state=42, class_weight="balanced"
            )
            validation_model.fit(x_train, y_train)
            validation_accuracy = float(validation_model.score(x_test, y_test))
            validation_method = "stratified_holdout_25_percent"
        model.fit(x, y)
        trained_at = datetime.now(UTC).isoformat()
        metadata: dict[str, object] = {
            "model_version": MODEL_VERSION,
            "trained_at": trained_at,
            "sample_count": len(rows),
            "class_count": len(classes),
            "classes": classes,
            "validation_accuracy": validation_accuracy,
            "validation_method": validation_method,
            "feature_names": list(FEATURE_NAMES),
        }
        metadata["limitations"] = _limitations(metadata)
        self._bundle = {"model": model, "metadata": metadata}
        joblib.dump(self._bundle, self.path)
        return TrainingResponse(
            model_version=MODEL_VERSION,
            trained_at=trained_at,
            sample_count=len(rows),
            class_count=len(classes),
            classes=[cast(AlgorithmName, item) for item in classes],
            validation_accuracy=validation_accuracy,
            validation_method=validation_method,
            feature_names=list(FEATURE_NAMES),
            limitations=_limitations(metadata),
        )

    def recommend(self, image_id: str) -> RecommendationResponse:
        bundle = self._load()
        if bundle is None:
            raise AppError(
                "recommendation_model_not_trained",
                "Train the recommendation model before requesting a recommendation.",
                409,
            )
        image = get_validated_image(image_id)
        features, _, _ = extract_features(
            load_image_array(image.path),
            width=image.width,
            height=image.height,
            channels=image.channels,
            color_mode=image.color_mode,
            file_size_bytes=image.size_bytes,
        )
        feature_data = features.model_dump(mode="json")
        vector = np.asarray([_numeric_features(feature_data)], dtype=np.float64)
        model = cast(Any, bundle.get("model"))
        metadata = bundle.get("metadata")
        if not isinstance(metadata, dict) or model is None:
            raise AppError(
                "recommendation_model_invalid",
                "The trained model artifact is invalid.",
                500,
            )
        prediction = model.predict(vector)[0]
        probabilities_array = model.predict_proba(vector)[0]
        classes = [cast(AlgorithmName, str(item)) for item in model.classes_]
        probabilities: dict[AlgorithmName, float] = {
            cast(AlgorithmName, str(label)): float(probability)
            for label, probability in zip(classes, probabilities_array, strict=True)
        }
        importance_array = np.asarray(model.feature_importances_, dtype=np.float64)
        importance = {
            name: float(value)
            for name, value in zip(FEATURE_NAMES, importance_array, strict=True)
        }
        top_features = sorted(
            importance.items(), key=lambda item: item[1], reverse=True
        )[:3]
        explanation = (
            "The model selected "
            + str(prediction)
            + " because the most influential image features were "
            + ", ".join(name for name, _ in top_features)
            + "."
        )
        return RecommendationResponse(
            id=str(uuid4()),
            image_id=image_id,
            model_version=str(metadata["model_version"]),
            recommended_algorithm=cast(AlgorithmName, str(prediction)),
            confidence=float(max(probabilities.values())),
            probabilities=probabilities,
            features={name: float(feature_data[name]) for name in FEATURE_NAMES},
            feature_importance=importance,
            explanation=explanation,
            limitations=[
                str(item) for item in cast(list[object], metadata["limitations"])
            ],
            generated_at=datetime.now(UTC).isoformat(),
        )


recommendation_model_store = RecommendationModelStore(
    settings.model_dir / "recommendation.joblib"
)
