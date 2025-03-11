from fastapi import APIRouter, Depends, HTTPException, Form
from models import User
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel,EmailStr, Field
from typing import Annotated
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from passlib.context import CryptContext #paraloyu şifrelemek için algoritma
from jose import jwt,JWTError
from datetime import timedelta, datetime, timezone


router = APIRouter(
    prefix="/auth",  # API'nin URL yolu, yani endpointlerin başına auth koyulur
    tags=["Authentication"]  #Swaggerda başlık tagsler
)

#JWT encoding ve decoding işlemleri için
SECRET_KEY = "acoztm3revp1vfj7ld5sz2ndg5xp79r9fnr2p4hx2dy63h6a8efhj6rm54u8evh8"
ALGORITHM = "HS256"

def get_db():  #Bu fonksiyon bize veritabanını veriyor
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]  #Dependency Injection

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #bcrypt şifreleme algoritması
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  #token makanizmasını tanımladık

#request body
class UserRequest(BaseModel):
    email : str
    username : str
    first_name : str
    last_name : str
    password : str
    is_active : bool
    role : str
    phone_number : str

#Kullanıcı giriş şeması
class LoginSchema(BaseModel):
    email: EmailStr
    password: str

#Token şeması
class Token(BaseModel):
    access_token: str
    token_type: str

#Özel form yapısı (Swagger ile uyumlu olacak)
class OAuth2EmailRequestForm:
    def __init__(
        self,
        email: str = Form(..., alias="username"),  # Swagger'da "username" olarak görünecek
        password: str = Form(...)
    ):
        self.email = email
        self.password = password

#JWT(JSON Web Tokens) -encoding                                   #Ne zaman geçerliliğini kaybedecek
def create_access_token(email: str, user_id: int, role: str, expires_delta: timedelta ):
    payload = {'sub': email,'id': user_id, 'role': role} #sabit bir şey değil, istediğimiz özellikleri koyduk
    expires = datetime.now(timezone.utc) + expires_delta #sistem çalıştıktan sonra timedelta da verilen zaman kadar
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

#JWT(JSON Web Tokens) -decoding                     #Tokeni aldık
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Token çözümleme
        email: str = payload.get("sub")  # Email'i al
        user_id: int = payload.get("id")  # Kullanıcı ID'sini al
        role: str = payload.get("role")  # Kullanıcı rolünü al

        if email is None or user_id is None:
              raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"email": email, "id": user_id, "role": role}  # Kullanıcı bilgilerini döndür
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


#Kullacıyı doğrulamak için
def authenticate_user(email : str, password : str,db):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

#Kullanıcı oluşturma
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,user_request : UserRequest):
    user = User(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        is_active = user_request.is_active,
        role = user_request.role,
        hashed_password = bcrypt_context.hash(user_request.password), #parola,veritabanında şifrelenerek tutulur. Şifre olarak yani
        phone_number = user_request.phone_number
    )
    db.add(user)
    db.commit()


#Kullanıcı giriş yaparak token alma
@router.post("/token", response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: OAuth2EmailRequestForm = Depends()):
    user = authenticate_user(form_data.email, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=60)) #email ile token oluşturduk
    return {"access_token": token, "token_type": "bearer"}
