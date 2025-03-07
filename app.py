from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from worker import process_task, get_completed_tasks

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.json
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    task = process_task.delay(prompt)
    return jsonify({"task_id": task.id})

@app.route("/task_status", methods=["GET"])
def task_status():
    return jsonify({"completed_tasks": get_completed_tasks()})

if __name__ == "__main__":
    app.run(debug=True)

