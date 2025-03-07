from celery import Celery
import httpx
from database import SessionLocal, Task

# Konfigurasi Celery tanpa Redis (gunakan local queue)
celery_app = Celery("tasks", broker="memory://", backend="database://")

@celery_app.task
def process_task(task_id: int, job_type: str):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    task.status = "processing"
    db.commit()

    try:
        # Simulasi API request berdasarkan job_type
        if job_type == "server_info":
            response = httpx.get("https://api.publicapis.org/entries")
            task.result = response.json()["count"]
        elif job_type == "weather":
            response = httpx.get("https://api.weatherapi.com/v1/current.json?key=YOUR_KEY&q=London")
            task.result = response.json()["current"]["temp_c"]
        else:
            task.result = "Unknown job type"
        
        task.status = "completed"
    except Exception as e:
        task.status = "failed"
        task.result = str(e)

    db.commit()
    db.close()
