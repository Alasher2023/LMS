from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.db import SQLite_DB
from typing import Optional, List

router = APIRouter(
    tags=["wrong_question_book"],
    prefix="/wrong_question_book",
)

@router.get("/")
def get_wrong_questions(
    session: SQLite_DB.SessionDep,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[SQLite_DB.WrongQuestion]:
    
    query = select(SQLite_DB.WrongQuestion)

    if subject and subject != '0':
        query = query.where(SQLite_DB.WrongQuestion.subject == subject)
    if difficulty and difficulty != '0':
        query = query.where(SQLite_DB.WrongQuestion.difficulty == difficulty)
    if tag:
        # Assuming tags are stored as comma-separated strings
        query = query.where(SQLite_DB.WrongQuestion.tags.like(f"%{tag}%"))

    wrong_questions = session.exec(query).all()
    
    return wrong_questions
