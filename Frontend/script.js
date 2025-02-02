const sendButton = document.getElementById('sendButton');
const userInput = document.getElementById('userInput');
const resultList = document.getElementById('result');
sendButton.addEventListener("click", sendMessage);

// Array para almacenar los últimos diez mensajes
let messageHistory = [];

async function sendMessage() {
  sendButton.disabled = true;
  let userText = userInput.value;

  if (!userText.trim()) {
    alert("Por favor, ingresa un mensaje antes de enviar.");
    sendButton.disabled = false;
    return;
  }

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
      resultMessage = (await response.json()).respuesta;
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

  // Formato para la pregunta y la respuesta como elementos separados
  const questionItem = `${timestamp} - Pregunta: ${userText}`;
  const responseItem = `${resultMessage}`;

  // Actualizar el array con los últimos diez mensajes
  messageHistory.push({ question: questionItem, response: responseItem });
  if (messageHistory.length > 10) {
    messageHistory.shift(); // Eliminar el mensaje más antiguo si hay más de 10
  }

  // Mostrar los mensajes como elementos de lista
  updateMessageList();
  sendButton.disabled = false;
  userInput.value = ''; // Limpiar el campo de entrada
}

function updateMessageList() {
  // Limpiar la lista actual
  resultList.innerHTML = '';

  // Agregar cada pregunta y respuesta al final del <ul>
  messageHistory.forEach(entry => {
    // Crear elemento para la pregunta
    const questionItem = document.createElement('li');
    questionItem.textContent = entry.question;
    questionItem.style.fontWeight = 'bold'; // Destacar la pregunta

    // Agregar pregunta al inicio de la lista
    resultList.prepend(questionItem);

    // Dividir la respuesta en líneas, filtrando vacíos
    const responseLines = entry.response.split("\n").filter(line => line.trim() !== "");

    responseLines.forEach((line, index) => {
      // Dividir aún más cada línea en partes usando " | "
      const responses = line.split(" | ").filter(text => text.trim() !== "");

      responses.forEach(responseText => {
        const responseItem = document.createElement('li');
        responseItem.textContent = responseText;
        resultList.prepend(responseItem);
      });

      // Agregar línea de asteriscos después de cada línea de la respuesta
      if (index < responseLines.length - 1) {
        const separatorItem = document.createElement('li');
        separatorItem.textContent = "**********";
        separatorItem.style.fontStyle = "italic"; // Opcional: poner en cursiva
        resultList.prepend(separatorItem);
      }
    });
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
