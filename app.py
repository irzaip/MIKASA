from flask import Flask, render_template, request, jsonify
import pickle
import redis
from worker import process_task

app = Flask(__name__)

# Database sederhana menggunakan dictionary
database = {}

# Redis client untuk tracking task
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Jenis tugas yang bisa dipilih
TASK_TYPES = ["Text Generation", "Summarization", "Translation", "Question Answering"]

# Fungsi untuk menyimpan database ke file pickle
def save_to_file(filename):
    with open(filename, "wb") as f:
        pickle.dump(database, f)

# Fungsi untuk memuat database dari file pickle
def load_from_file(filename):
    global database
    try:
        with open(filename, "rb") as f:
            database = pickle.load(f)
        return True
    except FileNotFoundError:
        return False

# API untuk mengambil semua data proyek
@app.route("/get_entries", methods=["GET"])
def get_entries():
    return jsonify(database)

# API untuk menambahkan entri baru
@app.route("/add_entry", methods=["POST"])
def add_entry():
    data = request.json
    project_name = data.get("project_name")
    task_type = data.get("task_type")
    prompt = data.get("prompt")
    parameters = data.get("parameters")

    if not project_name or not task_type or not prompt:
        return jsonify({"error": "All fields are required"}), 400

    entry_id = len(database) + 1
    database[entry_id] = {
        "project_name": project_name,
        "task_type": task_type,
        "prompt": prompt,
        "parameters": parameters,
        "status": "Pending"
    }
    return jsonify({"success": True, "id": entry_id})

# API untuk mengedit entri
@app.route("/edit_entry/<int:entry_id>", methods=["POST"])
def edit_entry(entry_id):
    if entry_id not in database:
        return jsonify({"error": "Entry not found"}), 404

    data = request.json
    database[entry_id].update({
        "project_name": data.get("project_name"),
        "task_type": data.get("task_type"),
        "prompt": data.get("prompt"),
        "parameters": data.get("parameters")
    })
    return jsonify({"success": True})

# API untuk menghapus entri
@app.route("/delete_entry/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    if entry_id in database:
        del database[entry_id]
        return jsonify({"success": True})
    return jsonify({"error": "Entry not found"}), 404

# API untuk menyimpan database ke file
@app.route("/save_data", methods=["POST"])
def save_data():
    data = request.json
    filename = data.get("filename", "default.pkl")
    save_to_file(filename)
    return jsonify({"success": True, "message": f"Data saved to {filename}"})

# API untuk memuat database dari file
@app.route("/load_data", methods=["POST"])
def load_data():
    data = request.json
    filename = data.get("filename", "default.pkl")
    if load_from_file(filename):
        return jsonify({"success": True, "message": f"Data loaded from {filename}"})
    return jsonify({"error": "File not found"}), 404

# API untuk menjalankan semua task dalam database
@app.route("/run_tasks", methods=["POST"])
def run_tasks():
    for entry_id, entry in database.items():
        task = process_task.delay(entry["prompt"])
        database[entry_id]["status"] = "Processing"
    return jsonify({"success": True, "message": "All tasks started"})

@app.route("/")
def index():
    return render_template("index.html", task_types=TASK_TYPES)

if __name__ == "__main__":
    app.run(debug=True)
