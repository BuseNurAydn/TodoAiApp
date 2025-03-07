from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from models import User
from sqlalchemy.testing import db
from pydantic import BaseModel , Field
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext #paraloyu şifrelemek için algoritma


router = APIRouter(
    prefix="/auth",  # API'nin URL yolu, yani endpointlerin başına auth koyulur
    tags=["Authentication"]  #Swaggerda başlık tagsler
)

def get_db():  #Bu fonksiyon bize veritabanını veriyor
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]  #Dependency Injection

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #bcrypt şifreleme algoritması

#request body
class UserRequest(BaseModel):
    email : str
    username : str
    first_name : str
    last_name : str
    password : str
    is_active : bool
    role : str


#Kullacıyı doğrulamak için
def authenticate_user(email : str, password : str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,user_request : UserRequest):
    user = User(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        is_active = user_request.is_active,
        role = user_request.role,
        hashed_password = bcrypt_context.hash(user_request.password) #parola,veritabanında şifrelenerek tutulur. Şifre olarak yani
    )
    db.add(user)
    db.commit()


