import celery
import redis
import openai
from flask import Flask, request, jsonify

# Konfigurasi OpenAI API
openai.api_key = "your-openai-api-key"

# Konfigurasi Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Konfigurasi Celery
celery_app = celery.Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@app.route("/start_task/<int:entry_id>", methods=["POST"])
def start_task(entry_id):
    if entry_id in database:
        database[entry_id]["status"] = "In Progress"
        redis_client.set(f"task:{entry_id}", "In Progress")
        process_task.apply_async(args=[entry_id])  # Jalankan task di background
        return jsonify({"success": True})
    return jsonify({"error": "Task not found"}), 404

@app.route("/check_task_status/<int:entry_id>", methods=["GET"])
def check_task_status(entry_id):
    status = redis_client.get(f"task:{entry_id}")
    if status:
        return jsonify({"status": status.decode("utf-8")})
    return jsonify({"status": "Pending"})