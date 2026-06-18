import pytest
from app.config import setting
from app.schemas import user, token
from jose import jwt
from tests.database import client, session

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

def test_create_user(client):
    response = client.post("/users/", json={"email": "abdullah@gmail.com", "password": "abdullah1234"})
    new_user = user.UserResponse(**response.json())
    assert response.status_code == 201
    assert new_user.email == "abdullah@gmail.com"

def test_login_user(client,create_test_user):
    response = client.post("/login", data={"username": create_test_user["email"], "password": create_test_user["password"]})
    login_response=token.Token(**response.json())
    payload = jwt.decode(login_response.access_token, setting.secret_key, algorithms=[setting.algorithm])
    id=payload.get("id")
    assert id == create_test_user["id"]
    assert login_response.token_type == "bearer"
    assert response.status_code==200
