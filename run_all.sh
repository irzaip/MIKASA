#!/bin/bash

echo "Starting Redis Server..."
redis-server &  # Menjalankan Redis di background
sleep 3         # Tunggu 3 detik agar Redis siap

echo "Starting Celery Worker..."
celery -A worker.celery_app worker --loglevel=info &  # Menjalankan Celery di background
sleep 5  # Tunggu agar Celery siap

echo "Starting Flask API..."
python app.py &  # Menjalankan Flask API di background
sleep 2

# Buka browser secara otomatis (opsional, hapus jika tidak perlu)
# xdg-open http://127.0.0.1:5000/

echo "All services started successfully!"
wait  # Menunggu semua proses selesai
