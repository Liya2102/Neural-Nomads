async function sendMessage() {
  let input = document.getElementById("chat-input");
  let message = input.value.trim();
  if (!message) return;

  let messagesDiv = document.getElementById("chat-messages");
  messagesDiv.innerHTML += `<p><b>You:</b> ${message}</p>`;

  let response = await fetch("/chatbot", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  });

  let data = await response.json();
  messagesDiv.innerHTML += `<p><b>Bot:</b> ${data.reply}</p>`;
  input.value = "";
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}