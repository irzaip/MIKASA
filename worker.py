import celery
import redis
import openai
from flask import Flask, request, jsonify
import time
import requests
import io
import base64
from PIL import Image
import datetime

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



@celery_app.task
def txt2img(prompt: str):
    url = "http://127.0.0.1:42003"
    requests.get(url=f"{url}/sdapi/v1/sd-models")
    option_payload = {
        "sd_model_checkpoint": "Flux1-Dev BNB NF4 v2.safetensors",
        "CLIP_stop_at_last_layers": 2
    }
    requests.post(url=f"{url}/sdapi/v1/options", json=option_payload)
    payload = {
        "prompt": prompt,
        "batch_size": 1,
        "steps": 20,
        "seed": -1,
        "distilled_cfg_scale": 3.5,
        "cfg_scale": 1,
        "width": 1024,
        "height": 1024,
        "sampler_name": "Euler",
        "scheduler": "Simple"
    }
    response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)
    r = response.json()
    x = 1
    i = r['images'][0]
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
    out_file = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    image.save(f"output/{out_file}.jpg")
    return print("Done task")