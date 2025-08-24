from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import  select
from app.db import SQLite_DB

router = APIRouter(
    tags=["paper"],
    prefix="/paper",
)
@router.get("/")
def get_paper(
    author: str,
    type: str,
    status: str,
    subject: str,
    grade: str,
    session: SQLite_DB.SessionDep
) -> list[SQLite_DB.Paper]:
    
    query = select(SQLite_DB.Paper).where(
        SQLite_DB.Paper.grade == grade
    )

    if subject != '0':
        query = query.where(SQLite_DB.Paper.subject == subject)
    if author != '0':
        query = query.where(SQLite_DB.Paper.author == author)
    if type != '0':
        query = query.where(SQLite_DB.Paper.type == type)
    if status != '0':
        query = query.where(SQLite_DB.Paper.status == status)
    
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
    updateTarget = session.exec(select(SQLite_DB.Paper).where(SQLite_DB.Paper.id == paper.id)).first()

    updateTarget.title = paper.title
    updateTarget.path = paper.path
    updateTarget.subject = paper.subject
    updateTarget.grade = paper.grade
    updateTarget.memo = paper.memo
    updateTarget.status = paper.status
    updateTarget.type = paper.type
    updateTarget.author = paper.author
    
    session.add(updateTarget)
    session.commit()
    session.refresh(updateTarget)
    
   
    return {"status": "200", "message": "Paper updated successfully"}

@router.delete("/{id}/")
def delete_paper(id: int, session: SQLite_DB.SessionDep):
    # 查询要删除的记录
    paper = session.get(SQLite_DB.Paper, id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # 删除记录
    session.delete(paper)
    session.commit()
    
    return {"status": "200", "message": "Paper deleted successfully"}


