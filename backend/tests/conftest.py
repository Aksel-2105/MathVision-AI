from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.experiments import Experiment, ExperimentRun
from app.db.session import get_db
from app.main import app
from app.services.analysis_service import analysis_store
from app.services.image_service import image_store
from app.services.processing_service import processing_store
from app.services.recommendation_service import recommendation_model_store

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False
)
Base.metadata.create_all(test_engine)


@pytest.fixture()
def client() -> TestClient:
    def override_get_db() -> Iterator[object]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_phase_two_stores() -> Iterator[None]:
    db = TestingSessionLocal()
    db.execute(delete(ExperimentRun))
    db.execute(delete(Experiment))
    db.commit()
    db.close()
    image_store.clear()
    analysis_store.clear()
    processing_store.clear()
    recommendation_model_store.clear()
    yield
    image_store.clear()
    analysis_store.clear()
    processing_store.clear()
    recommendation_model_store.clear()
    db = TestingSessionLocal()
    db.execute(delete(ExperimentRun))
    db.execute(delete(Experiment))
    db.commit()
    db.close()
