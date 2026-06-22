from urllib import response

import pytest
from typing import List
from pydantic import TypeAdapter
from app.schemas import PostResponse
from app.schemas.post import PostVote
from tests.conftest import authorize_client

def test_get_all_posts(authorize_client,test_posts):
    response = authorize_client.get("/posts/")
    posts = TypeAdapter(List[PostResponse]).validate_python(response.json())
    assert response.status_code == 200
    assert len(posts) == len(test_posts)

def test_unauthorized_get_all_post(client,test_posts):
    response=client.get("/posts/")
    assert response.status_code == 401

def test_unauthorized_get_one_post(client,test_posts):
    response=client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_get_one_post_not_exit(authorize_client):
    response=authorize_client.get(f"/posts/-9999")
    assert response.status_code == 404

def test_get_one_post(authorize_client,test_posts):
    response=authorize_client.get(f"/posts/{test_posts[0].id}")
    post=PostVote(**response.json())
    assert post.id == test_posts[0].id
    
@pytest.mark.parametrize("title, content, published", [
    ("MHA","Anime of the Year",True),
    ("To be Hero X","Can be Considerd to be Anime of the Year",True),
    ("Wind Breaker","Watched",False)])
def test_create_post(authorize_client,title,content,published,create_test_user):
    response =authorize_client.post("/posts/",json={"title": title, "content": content, "published": published})
    created_post = PostResponse(**response.json())
    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == create_test_user['id']
    
def test_unauthorized_user_create_post(client,test_posts):
    response = client.post("/posts/",json={"title": "Anime", "content": "Worth Watching", "published": True})
    assert response.status_code == 401

def test_unauthorized_delete_post(client,test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_delete_post(authorize_client,test_posts):
    response = authorize_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204

def test_delete_post_non_exit(authorize_client,test_posts):
    response = authorize_client.delete("/posts/-9999")
    assert response.status_code == 404

def test_delete_other_user_post(authorize_client,test_posts):
    response = authorize_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403

def test_update_post(authorize_client,test_posts):
    data = {
        "title": "MHA",
        "content": "Anime of the Year",
        "id": test_posts[0].id
        }
    response = authorize_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = PostResponse(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data["title"]

def test_other_user_post(authorize_client,test_posts):
    data = {
        "title": "MHA",
        "content": "Anime of the Year",
        "id": test_posts[3].id
    }
    response = authorize_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert response.status_code == 403

def test_patch_post(authorize_client,test_posts):
    data = {
        "title": "MHA",
    }
    response = authorize_client.patch(f"/posts/{test_posts[0].id}", json=data)
    updated_post = PostResponse(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data["title"]

def test_unauthorized_update_post(client,test_posts):
    response = client.put(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_unauthorized_patch_update_post(client,test_posts):
    response = client.patch(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

def test_update_post_non_exit(authorize_client,test_posts):
    data = {"title": "MHA", "content": "Anime of the Year"}
    response = authorize_client.put("/posts/-9999", json=data)
    assert response.status_code == 404

def test_patch_update_post_non_exit(authorize_client,test_posts):
    data = {"title": "MHA"}
    response = authorize_client.patch("/posts/-9999", json=data)
    assert response.status_code == 404