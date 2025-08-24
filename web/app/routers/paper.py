from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, or_
from app.db import SQLite_DB
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(
    tags=["paper"],
    prefix="/paper",
)

class PaperStatusUpdate(BaseModel):
    status: str

# Define academic types
ACADEMIC_TYPES = ['1', '2', '3', '4', '5']

@router.get("/")
def get_paper(
    session: SQLite_DB.SessionDep,
    author: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    academic_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list[SQLite_DB.Paper]:
    
    query = select(SQLite_DB.Paper)

    if grade and grade != '0':
        query = query.where(SQLite_DB.Paper.grade == grade)
    if subject and subject != '0':
        query = query.where(SQLite_DB.Paper.subject == subject)
    if author and author != '0':
        query = query.where(SQLite_DB.Paper.author == author)
    if type and type != '0':
        query = query.where(SQLite_DB.Paper.type == type)
    if status and status != '0':
        query = query.where(SQLite_DB.Paper.status == status)

    if academic_only:
        query = query.where(SQLite_DB.Paper.type.in_(ACADEMIC_TYPES))

    if start_date and end_date:
        query = query.where(
            or_(
                (SQLite_DB.Paper.due_date >= start_date),
                (SQLite_DB.Paper.next_review_date >= start_date)
            ),
            or_(
                (SQLite_DB.Paper.due_date <= end_date),
                (SQLite_DB.Paper.next_review_date <= end_date)
            )
        )

    papers = session.exec(query).all()
    
    return papers

@router.post("/")
def create_paper(
    session: SQLite_DB.SessionDep,
    paper: SQLite_DB.Paper
) -> SQLite_DB.Paper:
    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper

@router.put("/")
def update_paper(
    session: SQLite_DB.SessionDep,
    paper: SQLite_DB.Paper
):
    updateTarget = session.get(SQLite_DB.Paper, paper.id)
    if not updateTarget:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper_data = paper.model_dump(exclude_unset=True)
    for key, value in paper_data.items():
        setattr(updateTarget, key, value)
    
    session.add(updateTarget)
    session.commit()
    session.refresh(updateTarget)
    
    return {"status": "200", "message": "Paper updated successfully"}

@router.put("/{paper_id}/status")
def update_paper_status(paper_id: int, status_update: PaperStatusUpdate, session: SQLite_DB.SessionDep):
    paper = session.get(SQLite_DB.Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    paper.status = status_update.status
    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper

@router.delete("/{id}/")
def delete_paper(id: int, session: SQLite_DB.SessionDep):
    paper = session.get(SQLite_DB.Paper, id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    session.delete(paper)
    session.commit()
    
    return {"status": "200", "message": "Paper deleted successfully"}


