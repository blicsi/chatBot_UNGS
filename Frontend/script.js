document.getElementById('sendButton').addEventListener("click", sendMessage);
const userInput = document.getElementById('userInput');
const resultList = document.getElementById('result');

// Array para almacenar los últimos tres mensajes
let messageHistory = [];

async function sendMessage() {
  let userText = userInput.value;

  const url = "http://localhost:5000/ia";
  let response = await fetch(url, {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mensaje: userText
    })
  });

  let resultMessage;
  switch (response.status) {
    case 200:
      const responseData = await response.json();
      resultMessage = `${responseData.respuesta}`;
      break;
    case 400:
      resultMessage = "La búsqueda necesita más detalles.";
      break;
    case 500:
      resultMessage = "Hubo un error interno en el servidor.";
      break;
    default:
      resultMessage = `Error ${response.status}`;
      break;
  }

  // Agregar la hora al mensaje
  const now = new Date();
  const timestamp = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;
  const messageWithTime = `${timestamp} - ${resultMessage}`;

  // Actualizar el array con los últimos tres mensajes
  messageHistory.push(messageWithTime);
  if (messageHistory.length > 3) {
    messageHistory.shift(); // Eliminar el mensaje más antiguo si hay más de 3
  }

  // Mostrar los mensajes como elementos de lista
  updateMessageList();
}

function updateMessageList() {
  // Limpiar la lista actual
  resultList.innerHTML = '';

  // Agregar cada mensaje del historial como un elemento <li>
  messageHistory.forEach(message => {
    const listItem = document.createElement('li');
    listItem.textContent = message;
    resultList.appendChild(listItem);
  });
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
