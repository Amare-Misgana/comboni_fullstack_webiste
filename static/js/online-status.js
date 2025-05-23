// static/js/online-status.js

const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
const socketUrl = `${scheme}://${window.location.host}/ws/online/`;

console.log("★ will open WebSocket to:", socketUrl);
const onlineStatus = new WebSocket(socketUrl);

onlineStatus.onmessage = (e) => {
    console.log(JSON.parse(e.data))
    const { user, status } = JSON.parse(e.data);
    const dot = document.querySelector(`.${CSS.escape(user)} .online`);
    console.log(dot)
    if (dot) dot.style.display = status ? 'block' : 'none';

    // 2) show/hide the entire user‐card
    const card = document.querySelector(`.user.${CSS.escape(user)}`);
    if (card) {
        // status=true → make sure it’s visible
        // status=false → hide it entirely
        card.style.display = status ? '' : 'none';
    }
};

onlineStatus.onclose = () =>
    console.warn("Online-status socket closed unexpectedly");

