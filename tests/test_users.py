import pytest
from app.config import setting
from app.schemas import user, token
from jose import jwt

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

@pytest.mark.parametrize("email, password, status_code", [
    ("abdullah@gmail.com", "wrongpassword", 403),
    ("wrong@gmail.com",    "abdullah1234",  403),
    ("wrong@gmail.com",    "wrongpassword", 403),
    (None,                 None,            422),
    ("abdullah@gmail.com", None,            422),
    (None,                 "abdullah1234",  422),
    ("abdullah@gmail.com", "abdullah1234",  200),
])
def test_login_parametrized(client, create_test_user, email, password, status_code):
    response = client.post("/login", data={"username": email, "password": password})
    assert response.status_code == status_code