import json
import uuid  # Para generar identificadores únicos
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading
from Model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import torch

app = Flask(__name__)
CORS(app)

# ---------------IA---------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

intents = pd.read_csv("AI/dbs/databaseFinal.csv", encoding='utf-8', sep=",")
FILE = "AI/inteligencia.pth"
data = torch.load(FILE, map_location=torch.device('cpu'))

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Sam"
columna_preguntas = intents.iloc[:, 0].tolist()
columna_respuestas = intents.iloc[:, 1].tolist()

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.99999990:
        for intent in columna_preguntas:
            if tag == columna_preguntas.index(intent):
                respuesta = f"{str(bot_name)}: {str(columna_respuestas[tag])}"
        return respuesta
    else:
        return False

# ------------------------------
# Configuración inicial
MAX_WORKERS = 100
MIN_WORKERS = 1
executor = ThreadPoolExecutor(max_workers=MIN_WORKERS)
lock = threading.Lock()  # Bloqueo para acceso seguro a variables globales

# Diccionario para almacenar el estado de las tareas
tareas = {}

# -----------------------------
@app.route('/ia', methods=['POST'])
def chat():
    datos = json.loads(request.data)
    mensaje = datos.get('mensaje', '')

    if not mensaje:
        return jsonify({'error': 'El mensaje está vacío'}), 400

    tarea_id = str(uuid.uuid4())

    with lock:
        tareas[tarea_id] = {'estado': 'pendiente'}

    def procesar_mensaje():
        try:
            respuesta = get_response(mensaje)
            with lock:
                if not respuesta:
                    tareas[tarea_id] = {'estado': 'error', 'mensaje': 'No se generó una respuesta válida'}
                else:
                    tareas[tarea_id] = {'estado': 'completada', 'respuesta': respuesta}
        except Exception as e:
            with lock:
                tareas[tarea_id] = {'estado': 'error', 'mensaje': str(e)}

    executor.submit(procesar_mensaje)
    return jsonify({'tarea_id': tarea_id}), 202

# -----------------------------
@app.route('/tareas/<tarea_id>', methods=['GET'])
def obtener_estado_tarea(tarea_id):
    with lock:
        if tarea_id not in tareas:
            return jsonify({'error': 'Tarea no encontrada'}), 404
        return jsonify(tareas[tarea_id])

# -----------------------------
@app.route('/preguntas', methods=['GET'])
def obtener_preguntas():
    csv_file = 'AI/dbs/databaseFinalAutoCompletar.csv'

    try:
        df = pd.read_csv(csv_file, header=0)
        preguntas = df['Pregunta'].tolist()
        return jsonify(preguntas)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo CSV no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500

# -----------------------------
@app.route('/status', methods=['GET'])
def estado_servidor():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    with lock:
        return jsonify({
            "tareas_pendientes": len([t for t in tareas.values() if t['estado'] == 'pendiente']),
            "hilos_activos": executor._max_workers,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage
        })

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
