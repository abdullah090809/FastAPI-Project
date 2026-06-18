from app.schemas import user
from tests.database import client, session

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get('message') == "FastAPI Project"

def test_create_user(client):
    response = client.post("/users/", json={"email": "abdullah@gmail.com", "password": "abdullah1234"})
    new_user = user.UserResponse(**response.json())
    assert response.status_code == 201
    assert new_user.email == "abdullah@gmail.com"

def test_login_user(client):
    response = client.post("/login", data={"username": "abdullah@gmail.com", "password": "abdullah1234"})
    assert response.status_code==200
