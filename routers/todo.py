
from fastapi import APIRouter,Path,Depends,HTTPException
from typing import Annotated
from pydantic import BaseModel,Field
from models import Todo
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
#SessionLocal ile veritabanı ile bağlantı sağlayacağız
from routers.auth import get_current_user

router = APIRouter(
    prefix="/todo",   #API'nin URL yolu, yani endpointlerin başınatodo koyulur
    tags=["Todo"]   #Swaggerda başlık tagsler
)

#request body
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def get_db():  #Bu fonksiyon bize veritabanını veriyor
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]  #Dependency Injection
user_dependency = Annotated[dict, Depends(get_current_user)]

#get
@router.get("/")
async def read_all(user: user_dependency ,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()  #models klasöründe oluşturduğumuzTodo sınıfı #veritabanındaki tüm verileri getirir

@router.get("/get_by_id/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency ,todo_id : int = Path(gt=0)):
       todo = db.query(Todo).filter(Todo.id == todo_id).first()
       if todo is not None:
           return todo
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

#post
#post metodu oluştururken kendimize has request body oluşturmak en mantıklısı
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,db: db_dependency ,todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo)
    db.commit() #işlemin yapılacağı anlamına geliyor. commit demessek işlem yapılmaz

#update
@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db : db_dependency,todo_request: TodoRequest,todo_id: int = Path(gt=0)):
     todo = db.query(Todo).filter(Todo.id == todo_id).first()
     if todo is None :
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="Todo not found")

     todo.title = todo_request.title
     todo.description = todo_request.description
     todo.priority = todo_request.priority
     todo.complete = todo_request.complete

     db.add(todo)
     db.commit()

#delete
@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo (db: db_dependency,todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first() #id'ye göre todoyu aldık
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()