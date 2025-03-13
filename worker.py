import celery
import redis
import openai
from flask import Flask, request, jsonify
import time
#from langchain.chat_models import ChatOpenAI
#from langchain.schema import SystemMessage, HumanMessage

# Konfigurasi OpenAI API
openai.api_key = "your-openai-api-key"

# Konfigurasi Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Konfigurasi Celery
celery_app = celery.Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery_app.task
def working(input):
    print("I am working task:",input)
    time.sleep(5)
    print("I am done task:", input)
    
@celery_app.task
def doing_else(input):    
    print("I am working task:",input)
    time.sleep(5)
    print("I am done task:", input)
