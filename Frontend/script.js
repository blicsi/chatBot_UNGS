document.getElementById('sendButton').addEventListener("click", sendMessage)
const userInput = document.getElementById('userInput')
//const chatbox = document.getElementById('chatbox') 

async function sendMessage(){
  let userText = userInput.value

  const url = "http://localhost:5000/ia";
  let response = await fetch(url, {
    method: "POST",
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify({
      mensaje: userText
    })
  })
  let result
  switch (response.status){
      case 201:
        result = (await response.json()).respuesta;
        break;
      case 400:
        result = "La busqueda necesita mas detalles.";
        break;
      case 500:
        result = "Hubo un error interno en el servidor";
        break;
      default:
        result = "Error " + response.status;
        break;
    }
    // Actualizar el contenido del <p id="result">
  document.getElementById('result').textContent = result;
}

// ------------------------------------------

fetch('http://127.0.0.1:5000/preguntas')
.then(response => response.json())
.then(preguntas => {
    const lista = document.getElementById('preguntas-list');
    preguntas.forEach(pregunta => {
        const item = document.createElement('option');
        item.value = pregunta;
        lista.appendChild(item);
    });
})
.catch(error => console.error('Error al obtener las preguntas:', error));
