from fastapi import FastAPI,Path,Depends,HTTPException
from pydantic import BaseModel,Field
from models import Base , Todo
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from database import engine, SessionLocal
#SessionLocal ile veritabanı ile bağlantı sağlayacağız

app = FastAPI()

Base.metadata.create_all(bind=engine) #veritabanı yoksa oluşturur -> todoai_app.db

#request body
class TodoRequest(BaseModel):
    title : str = Field(min_length=3)
    description : str = Field(min_length=3, max_length=1000)
    priority : int = Field(gt=0, lt=6) #1-5
    complete : bool


def get_db():  #Bu fonksiyon bize veritabanını veriyor
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]  #Dependency Injection

#get
@app.get("/read_all")
async def read_all(db: db_dependency):
     return db.query(Todo).all()  #models klasöründe oluşturduğumuzTodo sınıfı #veritabanındaki tüm verileri getirir

@app.get("/get_by_id/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(db: db_dependency ,todo_id : int = Path(gt=0)):
       todo = db.query(Todo).filter(Todo.id == todo_id).first()
       if todo is not None:
           return todo
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

#post
#post metodu oluştururken kendimize has request body oluşturmak en mantıklısı
@app.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency ,todo_request: TodoRequest):
    todo = Todo(**todo_request.model_dump())
    db.add(todo)
    db.commit() #işlemin yapılacağı anlamına geliyor. commit demessek işlem yapılmaz

#update
@app.put("/update_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
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
@app.delete("/delete_todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo (db: db_dependency,todo_id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first() #id'ye göre todoyu aldık
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()