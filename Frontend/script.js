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

  let responseJSON = await response.json()
  console.log(responseJSON.respuesta)
}