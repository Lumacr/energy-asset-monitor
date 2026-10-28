
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database, models
from app.main import app


@pytest.fixture
def db_session():
    test_database_url = os.getenv("TEST_DATABASE_URL", "sqlite://")

    engine_options = {}

    if test_database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
        engine_options["poolclass"] = StaticPool

    test_engine = create_engine(
        test_database_url,
        **engine_options,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    models.Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[database.get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
