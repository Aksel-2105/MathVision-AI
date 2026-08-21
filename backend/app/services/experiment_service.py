import csv
import json
from datetime import UTC, datetime
from io import StringIO
from typing import Any, cast
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.db.models.experiments import Experiment, ExperimentRun
from app.imaging.features import extract_features
from app.imaging.io import load_image_array
from app.schemas.experiments import (
    ComparisonResponse,
    ComparisonRow,
    ExperimentDetail,
    ExperimentRunResponse,
    ExperimentSummary,
)
from app.schemas.processing import AlgorithmName, ProcessingResponse, QualityMetrics
from app.services.image_service import get_validated_image
from app.services.processing_service import processing_store

RANKING_POLICY = (
    "score = 0.50*SSIM + 0.35*min(PSNR/50, 1) + "
    "0.15*speed_score; speed_score=max(0, 1-execution_ms/5000)"
)


def _iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _run_response(run: ExperimentRun) -> ExperimentRunResponse:
    return ExperimentRunResponse(
        id=run.id,
        processing_id=run.processing_id,
        algorithm=cast(AlgorithmName, run.algorithm),
        parameters=run.parameters,
        metrics=QualityMetrics.model_validate(run.metrics),
        output_url=run.output_url,
        created_at=_iso(run.created_at),
    )


def _summary(experiment: Experiment) -> ExperimentSummary:
    return ExperimentSummary(
        id=experiment.id,
        name=experiment.name,
        description=experiment.description,
        source_image_id=experiment.source_image_id,
        source_image_name=experiment.source_image_name,
        created_at=_iso(experiment.created_at),
        updated_at=_iso(experiment.updated_at),
        run_count=len(experiment.runs),
    )


def _detail(experiment: Experiment) -> ExperimentDetail:
    return ExperimentDetail(
        **_summary(experiment).model_dump(),
        runs=[_run_response(run) for run in experiment.runs],
    )


def _get_experiment(db: Session, experiment_id: str) -> Experiment:
    experiment = db.scalar(
        select(Experiment)
        .options(selectinload(Experiment.runs))
        .where(Experiment.id == experiment_id)
    )
    if experiment is None:
        raise AppError(
            "experiment_not_found", "The requested experiment was not found.", 404
        )
    return experiment


def create_experiment(
    db: Session, image_id: str, name: str, description: str | None
) -> ExperimentSummary:
    image = get_validated_image(image_id)
    features, _, _ = extract_features(
        load_image_array(image.path),
        width=image.width,
        height=image.height,
        channels=image.channels,
        color_mode=image.color_mode,
        file_size_bytes=image.size_bytes,
    )
    experiment = Experiment(
        id=str(uuid4()),
        name=name.strip(),
        description=description.strip() if description else None,
        source_image_id=image.id,
        source_image_name=image.original_name,
        source_image_hash=image.content_hash,
        source_features=features.model_dump(mode="json"),
    )
    if not experiment.name:
        raise AppError(
            "invalid_experiment_name", "Experiment name cannot be empty.", 422
        )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return _summary(experiment)


def list_experiments(db: Session, image_id: str | None) -> list[ExperimentSummary]:
    statement = (
        select(Experiment)
        .options(selectinload(Experiment.runs))
        .order_by(Experiment.updated_at.desc())
    )
    if image_id:
        statement = statement.where(Experiment.source_image_id == image_id)
    return [_summary(item) for item in db.scalars(statement).all()]


def get_experiment(db: Session, experiment_id: str) -> ExperimentDetail:
    return _detail(_get_experiment(db, experiment_id))


def add_run(
    db: Session, experiment_id: str, processing_id: str
) -> ExperimentRunResponse:
    experiment = _get_experiment(db, experiment_id)
    processing = processing_store.get(processing_id).response
    if processing.image_id != experiment.source_image_id:
        raise AppError(
            "experiment_image_mismatch",
            "A processing result from another source image cannot be added.",
            422,
        )
    if any(run.processing_id == processing_id for run in experiment.runs):
        raise AppError(
            "duplicate_experiment_run",
            "This processing result is already part of the experiment.",
            409,
        )
    run = ExperimentRun(
        id=str(uuid4()),
        experiment_id=experiment.id,
        processing_id=processing.id,
        algorithm=processing.algorithm,
        parameters=processing.parameters,
        metrics=processing.metrics.model_dump(mode="json"),
        output_url=processing.output_url,
    )
    db.add(run)
    experiment.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(run)
    return _run_response(run)


def delete_experiment(db: Session, experiment_id: str) -> None:
    experiment = _get_experiment(db, experiment_id)
    db.delete(experiment)
    db.commit()


def _score(metrics: QualityMetrics) -> float:
    ssim_score = metrics.ssim if metrics.ssim is not None else 0.0
    psnr_score = min(max((metrics.psnr or 0.0) / 50.0, 0.0), 1.0)
    speed_score = max(0.0, 1.0 - metrics.execution_time_ms / 5000.0)
    return round(0.50 * ssim_score + 0.35 * psnr_score + 0.15 * speed_score, 6)


def _rank_rows(rows: list[ProcessingResponse]) -> list[ComparisonRow]:
    scored = [(processing, _score(processing.metrics)) for processing in rows]
    scored.sort(
        key=lambda item: (
            -item[1],
            -(item[0].metrics.ssim or -1.0),
            -(item[0].metrics.psnr or -1.0),
            item[0].metrics.execution_time_ms,
        )
    )
    return [
        ComparisonRow(
            processing_id=processing.id,
            algorithm=processing.algorithm,
            parameters=processing.parameters,
            metrics=processing.metrics,
            output_url=processing.output_url,
            rank=index,
            ranking_score=score,
        )
        for index, (processing, score) in enumerate(scored, start=1)
    ]


def compare_processing(processing_ids: list[str]) -> ComparisonResponse:
    processing = [processing_store.get(item).response for item in processing_ids]
    source_image_ids = {item.image_id for item in processing}
    if len(source_image_ids) != 1:
        raise AppError(
            "comparison_image_mismatch",
            "All processing results must use the same source image.",
            422,
        )
    return ComparisonResponse(
        source_image_id=processing[0].image_id,
        rows=_rank_rows(processing),
        ranking_policy=RANKING_POLICY,
    )


def compare_experiment(db: Session, experiment_id: str) -> ComparisonResponse:
    experiment = _get_experiment(db, experiment_id)
    rows = [
        ProcessingResponse(
            id=run.processing_id,
            image_id=experiment.source_image_id,
            algorithm=cast(AlgorithmName, run.algorithm),
            parameters=run.parameters,
            output_url=run.output_url,
            output_format="PNG",
            output_size_bytes=QualityMetrics.model_validate(
                run.metrics
            ).output_size_bytes,
            created_at=_iso(run.created_at),
            metrics=QualityMetrics.model_validate(run.metrics),
        )
        for run in experiment.runs
    ]
    return ComparisonResponse(
        source_image_id=experiment.source_image_id,
        rows=_rank_rows(rows),
        ranking_policy=RANKING_POLICY,
    )


def export_experiment(
    db: Session, experiment_id: str, file_format: str
) -> tuple[str, str]:
    detail = get_experiment(db, experiment_id)
    comparison = compare_experiment(db, experiment_id)
    payload: dict[str, Any] = {
        "experiment": detail.model_dump(mode="json"),
        "comparison": comparison.model_dump(mode="json"),
    }
    if file_format == "json":
        return json.dumps(payload, indent=2), "application/json"
    if file_format != "csv":
        raise AppError("invalid_export_format", "Use json or csv for export.", 422)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "rank",
            "processing_id",
            "algorithm",
            "mse",
            "rmse",
            "psnr",
            "ssim",
            "execution_time_ms",
            "output_size_bytes",
            "compression_ratio",
            "ranking_score",
        ]
    )
    for row in comparison.rows:
        writer.writerow(
            [
                row.rank,
                row.processing_id,
                row.algorithm,
                row.metrics.mse,
                row.metrics.rmse,
                row.metrics.psnr,
                row.metrics.ssim,
                row.metrics.execution_time_ms,
                row.metrics.output_size_bytes,
                row.metrics.compression_ratio,
                row.ranking_score,
            ]
        )
    return output.getvalue(), "text/csv"
