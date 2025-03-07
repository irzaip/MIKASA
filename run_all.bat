@echo off
echo Starting Redis Server...
start "" redis-server

timeout /t 3

echo Starting Celery Worker...
start "" cmd /k "celery -A worker.celery_app worker --loglevel=info"

timeout /t 5

echo Starting Flask API...
start "" cmd /k ".\env\Scripts\python app.py"

echo All services started successfully!
pause
