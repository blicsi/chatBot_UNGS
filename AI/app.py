import json
from flask import Flask, jsonify, request
from Chat import get_response

app = Flask(__name__)

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
if __name__ == '__main__':
   app.run(port=5000)

