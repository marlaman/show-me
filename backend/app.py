from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS, cross_origin
from llm_stuff import task_rru
from software_llm_stuff import task_rru_software

import pandas as pd
import numpy as np
import time
import uuid
import os
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3060"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Serve image from the backend folder
@app.route('/backend-image/<filename>', methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def serve_backend_image(filename):
    file_path = f"/Users/pranavmarla/ARCAssist/backend/{filename}"  # Path to your backend folder
    return send_file(file_path, mimetype='image/jpeg')  # Serve the image directly
    

def get_random_file(folder_path):
    try:
        # Get a list of files in the specified folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # Check if there are any files in the folder
        if not files:
            return "No files found in the folder."
        
        # Get a random file and return its full path
        random_file = random.choice(files)
        return os.path.join(folder_path, random_file)
    
    except FileNotFoundError:
        return "Folder not found."

    
def recursive_function(n, current_depth=1, max_depth=4, parent_id=None):
    node_id = str(uuid.uuid4())
    label = f"factorial({n}, id={node_id})"
    
    socketio.emit('update', {'id': node_id, 'label': label, 'parentId': parent_id})
    print("Current Depth: ", current_depth, " Node ID: ", node_id)
    
    time.sleep(2)
    if current_depth < max_depth:
        recursive_function(n * 2, current_depth + 1, max_depth, node_id)
        recursive_function(n * 2 + 1, current_depth + 1, max_depth, node_id)
    


@app.route('/recursive', methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def recursive():
    number = request.json['number']
    gh = recursive_function(number, current_depth=1, max_depth=4, parent_id=None)
    return jsonify({"status": "completed"})



@app.route('/self-healing', methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def self_healing():
    print("hello")
    question = request.json['question']
    answer = task_rru(question,socketio)
    return jsonify({"status": "completed", "answer" : answer})

@app.route('/self-healing-software', methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content-Type'])
def self_healing_software():
    print("hello")
    question = request.json['question']
    answer = task_rru_software(question,socketio)
    return jsonify({"status": "completed", "answer" : answer})





if __name__ == '__main__':
    socketio.run(app,port=5088, debug=True)
