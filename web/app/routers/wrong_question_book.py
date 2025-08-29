from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import select
from app.db import SQLite_DB
from typing import Optional, List
import shutil
import os
from datetime import datetime
import uuid
from pypdf import PdfWriter, PdfReader

# Import settings loader
from .settings import load_settings

router = APIRouter(
    tags=["wrong_question_book"],
    prefix="/wrong_question_book",
)

class GeneratePdfRequest(BaseModel):
    question_ids: List[int]

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

@router.post("/")
async def create_wrong_question(
    session: SQLite_DB.SessionDep,
    subject: str = Form(...),
    chapter: Optional[str] = Form(None),
    question_type: Optional[str] = Form(None),
    difficulty: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    review_at: Optional[str] = Form(None),
    question_file: Optional[UploadFile] = File(None),
    answer_file: Optional[UploadFile] = File(None),
):
    settings = load_settings()
    storage_path = settings.get('wrong_question_storage_path')

    if not storage_path or not os.path.isdir(storage_path):
        raise HTTPException(status_code=400, detail="Storage path is not configured or is not a valid directory.")

    question_file_path = None
    if question_file:
        question_filename = f"question_{datetime.now().strftime('%Y%m%d%H%M%S')}_{question_file.filename}"
        question_file_path = os.path.join(storage_path, question_filename)
        with open(question_file_path, "wb") as buffer:
            shutil.copyfileobj(question_file.file, buffer)

    answer_file_path = None
    if answer_file:
        answer_filename = f"answer_{datetime.now().strftime('%Y%m%d%H%M%S')}_{answer_file.filename}"
        answer_file_path = os.path.join(storage_path, answer_filename)
        with open(answer_file_path, "wb") as buffer:
            shutil.copyfileobj(answer_file.file, buffer)

    review_at_datetime = None
    if review_at:
        try:
            review_at_datetime = datetime.strptime(review_at, '%Y-%m-%d')
        except ValueError:
            pass # Or handle error appropriately

    new_question = SQLite_DB.WrongQuestion(
        subject=subject,
        chapter=chapter,
        question_type=question_type,
        difficulty=difficulty,
        tags=tags,
        review_at=review_at_datetime,
        question_path=question_file_path,
        answer_path=answer_file_path,
    )

    session.add(new_question)
    session.commit()
    session.refresh(new_question)

    return new_question

@router.delete("/{question_id}")
def delete_wrong_question(session: SQLite_DB.SessionDep, question_id: int):
    question = session.get(SQLite_DB.WrongQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Wrong question not found")

    # Delete associated files
    if question.question_path and os.path.exists(question.question_path):
        os.remove(question.question_path)
    if question.answer_path and os.path.exists(question.answer_path):
        os.remove(question.answer_path)

    session.delete(question)
    session.commit()
    return {"message": "Wrong question deleted successfully"}

@router.get("/file/{question_id}")
def get_wrong_question_file(session: SQLite_DB.SessionDep, question_id: int, type: str = 'question'):
    question = session.get(SQLite_DB.WrongQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Wrong question not found")

    file_path = None
    if type == 'question':
        file_path = question.question_path
    elif type == 'answer':
        file_path = question.answer_path
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

@router.post("/generate_pdf")
def generate_wrong_question_book(session: SQLite_DB.SessionDep, request: GeneratePdfRequest):
    A4_WIDTH = 595
    A4_HEIGHT = 842
    
    output_pdf = PdfWriter()

    questions_to_process = session.exec(select(SQLite_DB.WrongQuestion).where(SQLite_DB.WrongQuestion.id.in_(request.question_ids))).all()

    # --- Process Questions ---
    for question in questions_to_process:
        if not (question.question_path and os.path.exists(question.question_path)):
            continue
        
        try:
            reader = PdfReader(question.question_path)
            source_page = reader.pages[0]
            source_page.scale_to(A4_WIDTH, A4_HEIGHT)
            output_pdf.add_page(source_page)
        except Exception as e:
            print(f"Error processing question file {question.question_path}: {e}")

    # --- Process Answers ---
    for question in questions_to_process:
        if not (question.answer_path and os.path.exists(question.answer_path)):
            continue
            
        try:
            reader = PdfReader(question.answer_path)
            source_page = reader.pages[0]
            source_page.scale_to(A4_WIDTH, A4_HEIGHT)
            output_pdf.add_page(source_page)
        except Exception as e:
            print(f"Error processing answer file {question.answer_path}: {e}")

    # --- Save and Return ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TMP_DIR = os.path.join(BASE_DIR, '..', 'tmp')
    os.makedirs(TMP_DIR, exist_ok=True)

    filename = f"wrong_question_book_{uuid.uuid4()}.pdf"
    filepath = os.path.join(TMP_DIR, filename)

    with open(filepath, "wb") as f:
        output_pdf.write(f)

    return FileResponse(filepath, media_type='application/pdf', filename="wrong_question_book.pdf")
