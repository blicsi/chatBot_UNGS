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

# # ---------------IA---------------
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# intents = pd.read_csv("AI/dbs/databaseFinal.csv", encoding='utf-8', sep=",")
# FILE = "AI/inteligencia.pth"
# data = torch.load(FILE, map_location=torch.device('cpu'))

# input_size = data["input_size"]
# hidden_size = data["hidden_size"]
# output_size = data["output_size"]
# all_words = data["all_words"]
# tags = data["tags"]
# model_state = data["model_state"]

# model = NeuralNet(input_size, hidden_size, output_size).to(device)
# model.load_state_dict(model_state)
# model.eval()

# bot_name = "Sam"
# columna_preguntas = intents.iloc[:, 0].tolist()
# columna_respuestas = intents.iloc[:, 1].tolist()

# def get_response(msg):
#     sentence = tokenize(msg)
#     X = bag_of_words(sentence, all_words)
#     X = X.reshape(1, X.shape[0])
#     X = torch.from_numpy(X).to(device)

#     output = model(X)
#     _, predicted = torch.max(output, dim=1)
#     tag = tags[predicted.item()]

#     probs = torch.softmax(output, dim=1)
#     prob = probs[0][predicted.item()]

#     if prob.item() > 0.99999990:
#         for intent in columna_preguntas:
#             if tag == columna_preguntas.index(intent):
#                 respuesta = f"{str(bot_name)}: {str(columna_respuestas[tag])}"
#         return respuesta
#     else:
#         return False
# ------------------------------
# Configuración inicial


#------------------nueva respuesta---------------------------------
def get_response(pregunta):
    df = pd.read_csv("AI/dbs/databaseFinal.csv")  # Ajusta la ruta si es necesario

    # Convertir la columna de respuestas en listas separadas por " | "
    df["Respuesta"] = df["Respuesta"].str.split(" | ")

    # Convertir a diccionario
    mapa = dict(zip(df["Pregunta"], df["Respuesta"]))

    # Buscar la respuesta correspondiente a la pregunta
    return mapa.get(pregunta, "Pregunta no encontrada")

#------------------------------------------------------------------

# MAX_WORKERS = 100
# MIN_WORKERS = 1
# executor = ThreadPoolExecutor(max_workers=MIN_WORKERS)
# lock = threading.Lock()  # Bloqueo para acceso seguro a variables globales

# # Diccionario para almacenar el estado de las tareas
# tareas = {}

# -----------------------------
@app.route('/ia', methods=['POST'])
def chat():
    try:
        datos = request.get_json()

        if not datos or 'mensaje' not in datos:
            return jsonify({'error': 'El mensaje es obligatorio'}), 400

        mensaje = datos['mensaje']

        if not isinstance(mensaje, str) or not mensaje.strip():
            return jsonify({'error': 'El mensaje debe ser un texto no vacío'}), 400

        # Obtener respuesta directamente
        respuesta = get_response(mensaje)

        return jsonify({'respuesta': respuesta}), 200

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error inesperado: {str(e)}'}), 500
#--------------------------------------------------------------------------------

# @app.route('/tareas/<tarea_id>', methods=['GET'])
# def obtener_estado_tarea(tarea_id):
#     with lock:
#         if tarea_id not in tareas:
#             return jsonify({'error': 'Tarea no encontrada'}), 404
#         return jsonify(tareas[tarea_id])

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
# @app.route('/status', methods=['GET'])
# def estado_servidor():
#     cpu_usage = psutil.cpu_percent()
#     ram_usage = psutil.virtual_memory().percent
#     with lock:
#         return jsonify({
#             "tareas_pendientes": len([t for t in tareas.values() if t['estado'] == 'pendiente']),
#             "hilos_activos": executor._max_workers,
#             "cpu_usage": cpu_usage,
#             "ram_usage": ram_usage
#         })

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
