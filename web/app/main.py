from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from fastapi.responses import FileResponse
from app.db import SQLite_DB
from app.routers import paper

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
    # allow_origin_regex="http://.*:3000",
)
    
app.include_router(paper.router)
    
@app.on_event("startup")
async def startup():
    SQLite_DB.create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/test")
def root():
    return {"message": "Hello World Test"}

@app.get("/pdf")
async def root(filename: str):
    file_path = os.path.join("/Volumes/WD_8TB_1", filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, media_type="application/pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)