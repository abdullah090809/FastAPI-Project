from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Votes, Post
from app.oauth2 import Get_Current_User
from app.schemas import VoteBase

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote: VoteBase, db: Session = Depends(get_db), current_user: User = Depends(Get_Current_User)):
    post = db.query(Post).filter(Post.id==vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with {vote.post_id} does not Exit")
    else:
        vote_query=db.query(Votes).filter(Votes.post_id==vote.post_id,Votes.user_id==current_user.id)
        found_vote=vote_query.first()
        if vote.dir==1:
            if found_vote:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"User with id {current_user.id} has already voted on this Post")
            new_vote=Votes(post_id=vote.post_id,user_id=current_user.id)
            db.add(new_vote)
            db.commit()
            return{
                "message": "Successfully Voted"
            }
        else:
            if not found_vote:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vote does not Exit")
            vote_query.delete(synchronize_session=False)
            db.commit()
            return{
                "message": "Vote Successfully Deleted"
            }
    