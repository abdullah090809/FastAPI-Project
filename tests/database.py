from fastapi.testclient import TestClient
import pytest
from app.database import get_db, Base
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import setting


SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}:{setting.database_port}/{setting.database_name}_Test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionMaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionMaker()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)