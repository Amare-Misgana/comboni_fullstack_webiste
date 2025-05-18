const usernameToCheck = "target_username";
const statusDiv = document.getElementById("online-status");

const socket = new WebSocket("ws://" + window.location.host + "/wss/online");

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === "status" && data.user === usernameToCheck) {
        if (data.status === "online") {
            statusDiv.style.display = "inline-block"; // show when online
        } else {
            statusDiv.style.display = "none"; // hide when offline
        }
    }
};
