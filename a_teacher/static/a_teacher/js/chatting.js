// Get elements from DOM
const chatLog = document.getElementById('chat-log');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

// Get username from template (Django context)
const currentUser = JSON.parse(document.getElementById('me-username').textContent);
const otherUser = JSON.parse(document.getElementById('other-user').textContent);

// Establish WebSocket connection
const chatSocket = new WebSocket(
    `ws://${window.location.host}/ws/chat/${otherUser}/`
);

// Handle message reception
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const isCurrentUser = data.sender === currentUser;

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isCurrentUser ? 'sender' : 'receiver'}`;

    // Format timestamp
    const timestamp = new Date(data.timestamp).toLocaleTimeString();

    messageDiv.innerHTML = `
        <div class="message-header">
            <p>${data.message}</p>
            <p class="data">${timestamp}</p>
        </div>
    `;

    chatLog.appendChild(messageDiv);
};

// Handle message sending
function sendMessage() {
    console.log("I am clicked and sent message")
    const message = messageInput.value.trim();
    if (message) {
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        messageInput.value = '';
    }
}



// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Handle connection close
chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};