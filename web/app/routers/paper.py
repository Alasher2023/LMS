from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import  select
from app.db import SQLite_DB

router = APIRouter(
    tags=["paper"],
    prefix="/paper",
)
@router.get("/")
def get_paper(
    subject: str,
    grade: str,
    session: SQLite_DB.SessionDep
) -> list[SQLite_DB.Paper]:
    papers = session.exec(select(SQLite_DB.Paper)
                          .where(SQLite_DB.Paper.subject == subject,
                                 SQLite_DB.Paper.grade == grade)).all()
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


