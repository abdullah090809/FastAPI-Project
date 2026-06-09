from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlalchemy.orm import Session
from websockets import route
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.models import User
from app.utils import Hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
def create_user(user : UserCreate, db: Session = Depends(get_db)):
    user.password=Hash(user.password)
    new_user=User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    
    return new_user

@router.get("/",response_model=list[UserResponse])
def get_all_user(db: Session= Depends(get_db)):
    return db.query(User).all()

@router.get("/{id}",response_model=UserResponse)
def get_user(id: int,db: Session = Depends(get_db)):
    user=db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not Exit")
    return user
