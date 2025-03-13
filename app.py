from flask import Flask, render_template, request, jsonify
import pickle
import redis
import os

app = Flask(__name__)

# Inisialisasi Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Database menggunakan dictionary
database = {}

# Jenis tugas untuk dropdown
TASK_TYPES = ["Text Generation", "Summarization", "Translation", "Question Answering"]

# Fungsi untuk menyimpan database ke file pickle
def save_to_file(filename):
    with open(filename, "wb") as f:
        pickle.dump(database, f)

# Fungsi untuk memuat database dari file pickle
def load_from_file(filename):
    global database
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            database = pickle.load(f)
        return True
    return False

@app.route("/")
def index():
    return render_template("index.html", task_types=TASK_TYPES)

@app.route("/get_entries", methods=["GET"])
def get_entries():
    return jsonify(database)

@app.route("/add_entry", methods=["POST"])
def add_entry():
    data = request.json
    entry_id = len(database) + 1
    database[entry_id] = {
        "project_name": data.get("project_name"),
        "task_type": data.get("task_type"),
        "prompt": data.get("prompt"),
        "parameters": data.get("parameters"),
        "status": "Pending"
    }
    redis_client.set(f"task:{entry_id}", "Pending")
    return jsonify({"success": True, "id": entry_id, "entry": database[entry_id]})

@app.route("/edit_entry/<int:entry_id>", methods=["POST"])
def edit_entry(entry_id):
    if entry_id in database:
        data = request.json
        database[entry_id] = {
            "project_name": data.get("project_name"),
            "task_type": data.get("task_type"),
            "prompt": data.get("prompt"),
            "parameters": data.get("parameters"),
            "status": data.get("status")
        }
        redis_client.set(f"task:{entry_id}", data.get("status"))
        return jsonify({"success": True})
    return jsonify({"error": "Entry not found"}), 404

@app.route("/delete_entry/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    if entry_id in database:
        del database[entry_id]
        redis_client.delete(f"task:{entry_id}")
        return jsonify({"success": True})
    return jsonify({"error": "Entry not found"}), 404

@app.route("/save_data", methods=["POST"])
def save_data():
    filename = request.json.get("filename", "default.pkl")
    save_to_file(filename)
    return jsonify({"success": True, "message": f"Data saved to {filename}"})

@app.route("/load_data", methods=["POST"])
def load_data():
    filename = request.json.get("filename", "default.pkl")
    if load_from_file(filename):
        return jsonify({"success": True, "database": database})
    return jsonify({"error": "File not found"}), 404

@app.route("/start_process", methods=["POST"])
def start_process()
    filename = request.json.get("filename", "default.pkl")
    if load_from_file(filename):
        return print(filename)
    return jsonify({"error": "Starting error"})



if __name__ == "__main__":
    app.run(debug=True)

