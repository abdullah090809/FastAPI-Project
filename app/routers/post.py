from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy import Result, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post, User, Votes
from app.oauth2 import Get_Current_User
from app.schemas import PostCreate, PostUpdate, PostResponse, PostVote

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=list[PostVote])
def get_posts(db: Session = Depends(get_db),current_user: User= Depends(Get_Current_User),limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    results = (
        db.query(Post, func.count(Votes.post_id).label("votes"))
        .join(Votes, Votes.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .filter(Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    posts = []
    for post, vote_count in results:
        post.votes = vote_count
        posts.append(post)
    return posts
@router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User= Depends(Get_Current_User)):
    new_post = Post(owner_id=current_user.id,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=PostVote)
def get_post(id: int, db: Session = Depends(get_db),current_user: User= Depends(Get_Current_User)):
    result = (
        db.query(Post, func.count(Votes.post_id).label("votes"))
        .join(Votes, Votes.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .filter(Post.id == id)
        .first())
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    post,vote_count=result
    post.votes=vote_count
    return post

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: User = Depends(Get_Current_User)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to Perform this Action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, updated_post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(Get_Current_User)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to Perform this Action")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.patch("/{id}", response_model=PostResponse)
def update_post_patch(id: int, updated_post: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(Get_Current_User)):
    post_query = db.query(Post).filter(Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post.owner_id != current_user.id: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to Perform this Action")
    post_query.update(updated_post.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()
    return post_query.first()