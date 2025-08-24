from fastapi import Depends
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Annotated, AsyncGenerator, Optional
from datetime import datetime

class Paper(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    title: str
    subject: Optional[str] = Field(default=None)
    grade: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    path: Optional[str] = Field(default=None)
    memo: Optional[str] = Field(default=None)
    review_stage: Optional[int] = Field(default=0)
    next_review_date: Optional[datetime] = Field(default=None)
    last_reviewed_at: Optional[datetime] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)

path = "./app/db/database.db"
engine = create_engine(f"sqlite:///{path}",echo=True)

# ----------------- 数据库操作函数 -----------------
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


