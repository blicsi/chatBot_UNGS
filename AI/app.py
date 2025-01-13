import json
from flask import Flask, jsonify, request
from Chat import get_response
from flask_cors import CORS
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import psutil
import time

app = Flask(__name__)
CORS(app)

# Configuración del ThreadPoolExecutor dinámico
MAX_WORKERS = 200 # Máximo de hilos permitidos
MIN_WORKERS = 2   # Mínimo de hilos
executor = ThreadPoolExecutor(max_workers=MIN_WORKERS)

# Monitoreo de tareas en curso
tareas_en_proceso = 0

# -----------------------------
# Función para ajustar hilos dinámicamente
def ajustar_hilos():
    global executor
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent

    if cpu_usage < 50 and ram_usage < 70:
        nuevo_max_workers = min(MAX_WORKERS, executor._max_workers + 1)
    elif cpu_usage > 80 or ram_usage > 85:
        nuevo_max_workers = max(MIN_WORKERS, executor._max_workers - 1)
    else:
        nuevo_max_workers = executor._max_workers

    if nuevo_max_workers != executor._max_workers:
        executor._max_workers = nuevo_max_workers
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

    # Incrementar contador de tareas
    if tareas_en_proceso >= executor._max_workers:
        return jsonify({'error': 'Servidor sobrecargado, intente más tarde'}), 503

    tareas_en_proceso += 1

    # Función para procesar el mensaje
    def procesar_mensaje():
        global tareas_en_proceso
        try:
            respuesta = get_response(mensaje)
            if respuesta:
                return jsonify({'respuesta': respuesta}), 201
            else:
                return jsonify({'error': 'Falta más información'}), 400
        finally:
            tareas_en_proceso -= 1

    # Ejecutar la tarea en segundo plano
    future = executor.submit(procesar_mensaje)
    return jsonify({'status': 'Procesando mensaje'}), 202

# -----------------------------
@app.route('/preguntas', methods=['GET'])
def obtener_preguntas():
    # Ruta del archivo CSV
    csv_file = 'AI/dbs/databaseFinalAutoCompletar.csv'

    # Leer el archivo CSV con pandas
    try:
        df = pd.read_csv(csv_file, header=0)  # Asume que la primera fila es el encabezado
        preguntas = df['Pregunta'].tolist()  # Convertir a lista
        return jsonify(preguntas)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo CSV no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500

# -----------------------------
@app.route('/status', methods=['GET'])
def estado_servidor():
    # Monitorear la carga del sistema y tareas activas
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    return jsonify({
        "tareas_en_proceso": tareas_en_proceso,
        "hilos_activos": executor._max_workers,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage
    })

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
