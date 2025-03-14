
from fastapi import APIRouter,Path,Depends,HTTPException,Request
from typing import Annotated
from pydantic import BaseModel,Field
from starlette.responses import RedirectResponse
from models import Todo
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
#SessionLocal ile veritabanı ile bağlantı sağlayacağız
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todo",   #API'nin URL yolu, yani endpointlerin başınatodo koyulur
    tags=["Todo"]   #Swaggerda başlık tagsler
)

templates = Jinja2Templates(directory="templates")  #sayfaları bağlamak için

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

#Sayfalarımızı bağlıyoruz - Login ve Todo

##Logine yollama fonksiyonu
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get('id')).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()


# add todo button
@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request,"user": user})
    except:
        return redirect_to_login()


#edit todo button
@router.get("/edit-todo-page/{todo_id}")
async def render_add_todo_page(request: Request, todo_id : int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request": request,"todo": todo,"user": user})
    except:
        return redirect_to_login()

#get
@router.get("/")
async def read_all(user: user_dependency ,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()  #ilgili id'ye sahip, kullanıcıya ait todolar gözükür

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_by_id(user: user_dependency,db: db_dependency ,todo_id : int = Path(gt=0)):
       if user is None:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
       todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first() #güvenlik önlemi
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
async def update_todo(user:user_dependency,db : db_dependency,todo_request: TodoRequest,todo_id: int = Path(gt=0)):
     if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
     todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first() #güvenlik önlemi
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
async def delete_todo (user:user_dependency,db: db_dependency,todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo = db.query(Todo).filter(Todo.id == todo_id).filter(Todo.owner_id == user.get('id')).first() #güvenlik önlemi #id'ye göre todoyu aldık
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()