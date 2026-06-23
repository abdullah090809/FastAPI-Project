from fastapi.testclient import TestClient
import pytest
from app.database import get_db, Base
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import setting
from app.oauth2 import Create_Access_Token
from app.models import Post


SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.database_username}:{setting.database_password}@{setting.database_hostname}:{setting.database_port}/{setting.database_name}_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionMaker = sessionmaker(autoflush=False, autocommit=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionMaker()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def create_test_user(client):
    user_data={
        "email": "abdullah@gmail.com",
        "password": "abdullah1234"
    }
    response = client.post("/users/",json=user_data)
    assert response.status_code == 201
    new_user=response.json()
    new_user["password"]="abdullah1234"
    return new_user

@pytest.fixture
def create_test_user2(client):
    user_data = {
        "email": "ali@gmail.com",
        "password": "ali1234"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = "ali1234"
    return new_user

@pytest.fixture
def token(create_test_user):
    return Create_Access_Token({"id": create_test_user["id"]})

@pytest.fixture
def authorize_client(client,token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(create_test_user,create_test_user2,session):
        posts_data = [
            {"title": "first title", "content": "first content", "owner_id": create_test_user['id']},
            {"title": "2nd title",   "content": "2nd content",   "owner_id": create_test_user['id']},
            {"title": "3rd title",   "content": "3rd content",   "owner_id": create_test_user['id']},
            {"title": "3rd title",   "content": "3rd content",   "owner_id": create_test_user2['id']}
        ]
        def create_post(post):
            return Post(**post)
        post=map(create_post,posts_data)
        post=list(post)
        session.add_all(post)
        session.commit()
        posts=session.query(Post).all()
        return posts
     