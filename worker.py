import celery
import redis
import openai
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Konfigurasi OpenAI API
openai.api_key = "your-openai-api-key"

# Konfigurasi Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Konfigurasi Celery
celery_app = celery.Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

# Celery Task untuk memproses teks dengan GPT
@celery_app.task
def process_task(prompt):
    chat = ChatOpenAI(model_name="gpt-4")
    response = chat.invoke([SystemMessage(content="You are an assistant"), HumanMessage(content=prompt)])

    # Tambahkan task selesai ke Redis
    redis_client.incr("completed_tasks")

    return response.content

# API untuk mengambil jumlah task selesai
def get_completed_tasks():
    return int(redis_client.get("completed_tasks") or 0)

