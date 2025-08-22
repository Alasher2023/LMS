from fastapi import Depends
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Annotated, AsyncGenerator, Optional

class Paper(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    subject: str
    grade: str
    author: str | None = None
    type: str | None = None
    status: str | None = None
    title: str
    path: str
    memo: str | None = None

path = "./app/db/database.db"
engine = create_engine(f"sqlite:///{path}",echo=True)

# ----------------- 数据库操作函数 -----------------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


