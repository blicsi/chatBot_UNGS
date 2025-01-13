import json
import uuid  # Para generar identificadores únicos
from flask import Flask, jsonify, request
from Chat import get_response
from flask_cors import CORS
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import threading

app = Flask(__name__)
CORS(app)

# Configuración inicial
MAX_WORKERS = 20
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
