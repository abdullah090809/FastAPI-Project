from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.database import get_db
from app.models.users import User
from app.schemas.token import TokenData
from sqlalchemy.orm import Session
from app.config import setting

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY=setting.secret_key
ALGORITHM=setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=setting.access_token_expire_minutes

def Create_Access_Token(data: dict):
    payload=data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})

    encoded_jwt=jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def Verify_Access_Token(token: str, credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id=payload.get("id")
        if id is None:
            raise credentials_exception
        token_data=TokenData(**payload)
        return token_data
    except JWTError:
        raise credentials_exception

def Get_Current_User(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate Credentials",headers={"WWW-Authenticate": "Bearer"})
    
    token = Verify_Access_Token(token,credentials_exception)
    user=db.query(User).filter(User.id==token.id).first()
    return user
        