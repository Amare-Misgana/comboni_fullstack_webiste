const search = document.getElementById("user-search");
const users = document.querySelectorAll(".user");

search.addEventListener("input", () => {
    const searchValue = search.value.toLowerCase();

    users.forEach(user => {
        const name = user.querySelector("h3").textContent.toLowerCase();
        if (name.includes(searchValue)) {
            user.style.display = "";
        } else {
            user.style.display = "none";
        }
    });
});

let maxLengh = 8


document.addEventListener("DOMContentLoaded", () => {
    const users = document.querySelectorAll(".user");

    users.forEach(user => {
        const nameElement = user.querySelector("h3");
        if (nameElement) {
            const name = nameElement.textContent.trim();
            if (name.length > 2) {
                nameElement.textContent = name.slice(0, maxLengh) + "...";
            }
        }
    });
});


document.addEventListener('DOMContentLoaded', () => {
    new EmojiPicker({
        trigger: [
            {
                selector: '.emoji-btn',
                insertInto: '.message-input'
            }
        ],
        closeButton: true
    });
});


const btns = document.querySelectorAll('.chat-user-btn');
const users_card = document.querySelectorAll('.user');
const noneMsg = document.getElementById('no-users');

function applyFilter(role) {
    let any = false;
    users_card.forEach(u => {
        if (u.classList.contains(role)) {
            u.style.display = '';
            any = true;
        } else {
            u.style.display = 'none';
        }
    });
    noneMsg.style.display = any ? 'none' : '';
}

btns.forEach(btn =>
    btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const role = btn.id.replace('-btn', '');
        localStorage.setItem('chatRole', role);
        applyFilter(role);
    })
);

// on load
const saved = localStorage.getItem('chatRole') || 'student';
const startBtn = document.getElementById(saved + '-btn');
if (startBtn) startBtn.click();


