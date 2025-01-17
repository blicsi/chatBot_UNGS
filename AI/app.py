import json
import uuid  # Para generar identificadores únicos
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import threading
from Model import NeuralNet
from nltk_utils import bag_of_words,tokenize
import torch

app = Flask(__name__)
CORS(app)

#---------------IA---------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

intents = pd.read_csv("AI/dbs/databaseFinal.csv",encoding='utf-8',sep=",")

FILE="AI/inteligencia.pth"
data = torch.load(FILE, map_location=torch.device('cpu'))


input_size=data["input_size"]
hidden_size=data["hidden_size"]
output_size=data["output_size"]
all_words=data["all_words"]
tags=data["tags"]
model_state=data["model_state"]

model = NeuralNet(input_size,hidden_size,output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name="Sam"
columna_preguntas = intents.iloc[:, 0].tolist()
columna_respuestas = intents.iloc[:, 1].tolist()

def get_response(msg):
    sentence = tokenize(msg)
    X = bag_of_words(sentence,all_words)
    X = X.reshape(1,X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model (X)
    _, predicted = torch.max(output,dim=1)
    tag = tags [predicted.item()]

    probs = torch.softmax(output,dim=1)
    prob=probs[0][predicted.item()]

    if prob.item()>.99999990:
        for intent in columna_preguntas:
            if tag == columna_preguntas.index(intent):
                respuesta=f"{str(bot_name)}:{str(columna_respuestas[tag])}"
                #print(respuesta)
        return respuesta
    else:
        return False 

#------------------------------
# Configuración inicial
MAX_WORKERS = 100
MIN_WORKERS = 1
executor = ThreadPoolExecutor(max_workers=MIN_WORKERS)
lock = threading.Lock()  # Bloqueo para acceso seguro a variables globales
tareas_en_proceso = 0

# -----------------------------
def ajustar_hilos():
    """Ajusta dinámicamente los hilos del ThreadPoolExecutor según la carga del servidor."""
    global executor

    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent

    with lock:
        if cpu_usage < 50 and ram_usage < 70 and executor._max_workers < MAX_WORKERS:
            nuevo_max_workers = executor._max_workers + 1
        elif (cpu_usage > 80 or ram_usage > 85) and executor._max_workers > MIN_WORKERS:
            nuevo_max_workers = executor._max_workers - 1
        else:
            return  # No se necesita ajustar

        # Reiniciar el executor con el nuevo número de hilos
        executor.shutdown(wait=False)
        executor = ThreadPoolExecutor(max_workers=nuevo_max_workers)
        print(f"Hilos ajustados a: {nuevo_max_workers}")

# -----------------------------
@app.route('/ia', methods=['POST'])
def chat():
    global tareas_en_proceso

    # Leer datos del cuerpo de la solicitud
    datos = json.loads(request.data)
    mensaje = datos.get('mensaje', '')

    if not mensaje:
        return jsonify({'error': 'El mensaje está vacío'}), 400

    ajustar_hilos()

    with lock:
        if tareas_en_proceso >= executor._max_workers:
            return jsonify({'error': 'Servidor sobrecargado, intente más tarde'}), 503

        tarea_id = str(uuid.uuid4())
        tareas_en_proceso += 1

    def procesar_mensaje():
        """Función para procesar la respuesta de la IA."""
        global tareas_en_proceso  # Usamos global para modificar la variable global

        try:
            respuesta = get_response(mensaje)
            if not respuesta:
                return {'tarea_id': tarea_id, 'estado': 'error', 'mensaje': 'No se generó una respuesta válida'}
            return {'tarea_id': tarea_id, 'respuesta': respuesta, 'estado': 'completada'}
        except Exception as e:
            return {'tarea_id': tarea_id, 'estado': 'error', 'mensaje': str(e)}
        finally:
            with lock:
                tareas_en_proceso -= 1

    # Enviar la tarea al ThreadPoolExecutor y esperar su resultado
    future = executor.submit(procesar_mensaje)
    resultado = future.result()  # Aseguramos que esto devuelva un diccionario

    # Verificamos el resultado
    if 'estado' in resultado:
        if resultado['estado'] == 'completada':
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400  # En caso de error o respuesta inválida
    else:
        return jsonify({'error': 'Respuesta no esperada del servidor'}), 500

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
            "tareas_en_proceso": tareas_en_proceso,
            "hilos_activos": executor._max_workers,
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage
        })

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
