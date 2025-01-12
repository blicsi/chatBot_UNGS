import json
from flask import Flask, jsonify, request
from Chat import get_response
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/ia', methods=['POST'])
def chat():
    # Extraer datos del JSON enviado en el cuerpo del POST
    datos = json.loads(request.data)
    
    # Obtener el mensaje del usuario
    mensaje = datos.get('mensaje', '')  # Asume que el JSON tiene una clave 'mensaje'
    
    if not mensaje:
        return jsonify({'error': 'El mensaje está vacío'}), 400
    
    # Pasar el mensaje a la función get_response
    respuesta = get_response(mensaje)
    
    if respuesta:
        return jsonify({'respuesta': respuesta}), 201
    else:
        return jsonify({'error': 'falta mas informacion'}), 400

#-----------------------------

@app.route('/preguntas', methods=['GET'])
def obtener_preguntas():
    # Ruta del archivo CSV
    csv_file = 'AI\dbs\databaseFinalAutoCompletar.csv'
    
    # Leer el archivo CSV con pandas
    df = pd.read_csv(csv_file, header=0)  # Asume que la primera fila es el encabezado
    
    # Convertir la columna 'Pregunta' en una lista
    preguntas = df['Pregunta'].tolist()
    
    # Retornar la lista como JSON
    return jsonify(preguntas)

#-----------------------------
if __name__ == '__main__':
   app.run(debug=True)

