from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import FileResponse
from app.db import SQLite_DB
from app.routers import paper, dashboard
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlmodel import select, Session

# Ebbinghaus intervals in days
review_intervals = [1, 2, 4, 7, 15, 30, 60]

def review_papers():
    """
    Check for papers that are due for review and update their status.
    """
    with Session(SQLite_DB.engine) as session:
        papers_to_review = session.exec(
            select(SQLite_DB.Paper).where(
                SQLite_DB.Paper.status == "3",  # Status '3' means '已完成'
                SQLite_DB.Paper.next_review_date <= datetime.now()
            )
        ).all()

        for paper in papers_to_review:
            paper.status = "4"  # Status '4' means '未复习' (Pending Review)
            session.add(paper)

        session.commit()
        if papers_to_review:
            print(f"Checked for reviews at {datetime.now()}. Found {len(papers_to_review)} papers to review.")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
    "http://*:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paper.router)
app.include_router(dashboard.router)

@app.on_event("startup")
async def startup():
    SQLite_DB.create_db_and_tables()
    # Initialize scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(review_papers, 'interval', hours=12)
    scheduler.start()
    print("Scheduler started. The review job will run every 12 hours.")

@app.post("/paper/{paper_id}/complete")
def complete_paper(paper_id: int, session: SQLite_DB.SessionDep):
    """
    Mark a paper as completed for the first time, starting the review cycle.
    """
    paper = session.get(SQLite_DB.Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper.status = "3"  # Status '3' means '已完成'
    paper.review_stage = 0
    paper.last_reviewed_at = datetime.now()
    paper.next_review_date = datetime.now() + timedelta(days=review_intervals[0])

    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper

@app.post("/paper/{paper_id}/review")
def mark_as_reviewed(paper_id: int, session: SQLite_DB.SessionDep):
    """
    Mark a paper as reviewed, advancing its review stage.
    """
    paper = session.get(SQLite_DB.Paper, paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    paper.status = "3"  # Status '3' means '已完成'
    paper.review_stage += 1
    paper.last_reviewed_at = datetime.now()

    # If the review stage is within our defined intervals, set the next review date.
    if paper.review_stage < len(review_intervals):
        days_to_add = review_intervals[paper.review_stage]
        paper.next_review_date = datetime.now() + timedelta(days=days_to_add)
    else:
        # If all review cycles are complete, we'll just set the next_review_date to None.
        paper.next_review_date = None

    session.add(paper)
    session.commit()
    session.refresh(paper)
    return paper

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/pdf")
async def root(filename: str):
    file_path = os.path.join("/Volumes/WD_8TB_1", filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
