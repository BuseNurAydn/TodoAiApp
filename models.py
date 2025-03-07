#veritabanında tutulacak tablolar oluşturulacak. Kolonlar vs.

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Todo(Base):
    __tablename__ ='todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))  #Yabancı anahtar kullanarak ilişki kurduk. Bire çok ilişki

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)  #aynı emaille başka biri kayıt olmasın dedik
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)   #Şifrelenmiş parola
    is_active = Column(Boolean, default=True)
    role = Column(String)

#Todo, kullanıcı tarafından oluşturulacak. Her kullanıcının todo'su kendine ait.
#Bu yüzden todo'nun kime ait olduğunu bilmemiz gerekiyor. Tablolar arasında ilişki kurmamız gerekiyor