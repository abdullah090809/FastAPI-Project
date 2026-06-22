import pytest
from app.models import Votes
from app.schemas.vote import VoteBase

@pytest.fixture
def test_vote(test_posts,session,create_test_user):
    vote = {
        "post_id": test_posts[3].id,
        "user_id": create_test_user["id"]
    }
    new_vote=Votes(**vote)
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorize_client,test_posts):
    response = authorize_client.post("/vote",json={"post_id": test_posts[3].id, "dir": 1})
    response.status_code == 201

def test_vote_twice(authorize_client,test_posts,test_vote):
    response = authorize_client.post("/vote/",json={"post_id": test_posts[3].id, "dir": 1})
    assert response.status_code == 409

def test_unvote_on_post(authorize_client,test_posts,test_vote):
    response = authorize_client.post("/vote",json={"post_id": test_posts[3].id, "dir": 0})
    response.status_code == 201

def test_unvote_on_post_vote_does_not_exit(authorize_client,test_posts):
    response = authorize_client.post("/vote",json={"post_id": test_posts[3].id, "dir": 0})
    response.status_code == 404

def test_unvote_on_post_does_not_exit(authorize_client,test_posts):
    response = authorize_client.post("/vote",json={"post_id": -9999, "dir": 0})
    response.status_code == 404

def test_unauthorize_vote_on_post(client,test_posts):
    response = client.post("/vote",json={"post_id": test_posts[3].id, "dir": 1})
    response.status_code == 401