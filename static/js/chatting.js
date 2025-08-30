window.addEventListener('load', () => {
    chatLog.scrollTop = chatLog.scrollHeight;
});


// Get elements from DOM
const chatLog = document.getElementById('chat-log');
const sendButton = document.getElementById('send-button');

// Get username from template (Django context)
const currentUser = JSON.parse(document.getElementById('me-username').textContent);
const otherUser = JSON.parse(document.getElementById('other-user').textContent);


const roomName = JSON.parse(document.getElementById('room-name').textContent);


// Establish WebSocket connection 
const chatSocket = new WebSocket(
    `ws://${window.location.host}/ws/chat/${roomName}/`
);

// Handle message reception
chatSocket.onmessage = function (e) {

    if (document.querySelector(".no-message")) {
        document.querySelector(".no-message").style.display = "none"
    }


    const data = JSON.parse(e.data);

    const message = data.message
    const sender = data.sender
    let isCurrentUser = sender == currentUser

    // document.querySelector(`.{data.receiver}`).style.order = -1

    console.log(data.receiver)

    const messageDiv = document.createElement('div');
    messageDiv.className = `${isCurrentUser ? 'sender' : 'receiver'}`;

    // Format timestamp
    const timestamp = new Date(data.timestamp).toLocaleTimeString();

    messageDiv.innerHTML = `
            <p>${data.message}</p>
            <p class="data">${timestamp}</p>
    `;

    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;

};

const messageInput = document.getElementById('message-input');
function sendMessage() {
    const message = messageInput.value.trim();
    chatSocket.send(JSON.stringify({
        "message": message,
        "sender": currentUser,
        "receiver": otherUser,
    }))
    messageInput.value = '';
}

sendButton.addEventListener('click', sendMessage);


messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};