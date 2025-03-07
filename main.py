from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, Task
from tasks import process_task
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# UI Dashboard
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

# API untuk menambahkan tugas
class TaskRequest(BaseModel):
    job_type: str

@app.post("/add_task/")
async def add_task(task_request: TaskRequest, db: Session = Depends(get_db)):
    task = Task(job_type=task_request.job_type, status="pending")
    db.add(task)
    db.commit()
    db.refresh(task)

    # Kirim tugas ke Celery
    process_task.delay(task.id, task_request.job_type)
    return {"message": "Task added", "task_id": task.id}

# API untuk melihat status tugas
@app.get("/tasks/")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": [ {"id": t.id, "job_type": t.job_type, "status": t.status, "result": t.result} for t in tasks] }

# API menerima request dari server lain
@app.post("/external_task/")
async def external_task(task_request: TaskRequest, db: Session = Depends(get_db)):
    return await add_task(task_request, db)
