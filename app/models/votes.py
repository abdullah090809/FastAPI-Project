from sqlalchemy import Column, ForeignKey, Integer
from app.database import Base

class Votes(Base):
    __tablename__= "votes"
    user_id= Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    post_id= Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"),primary_key=True)