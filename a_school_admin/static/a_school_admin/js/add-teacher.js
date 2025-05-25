document
    .getElementById("teacher-profile")
    .addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            document.getElementById("teacher-preview").src = ev.target.result;
        };
        reader.readAsDataURL(file);
    });
document
    .querySelector(".add-teacher-form .submit-btn")
    .addEventListener("click", function (e) {
        const fileInput = document.getElementById("teacher-profile");
        if (!fileInput.files.length) {
            alert("Please select a profile picture.");
            e.preventDefault();
        }
    });

//   PASSWORD VALIDATOR

const password = document.getElementById("password");
const conf_password = document.getElementById("confirm_password");
const error_list = document.querySelector(".error-list");
const error_validator = document.querySelector(".error-card")



password.addEventListener("input", () => {
    if (conf_password.value == "" && document.getElementsByClassName("error-list-element").length < 1) {
        let new_list = document.createElement("li");
        new_list.classList.add("error-list-element", "error-child");
        new_list.textContent = "Confirm assword can't be empty!";
        error_list.appendChild(new_list);
    }
    if (conf_password.value.length != 0) {
        error_items = document.getElementsByClassName("error-list-element")
        Array.from(error_items).forEach(error => error.remove());
    }
    if (password.value == conf_password.value) {
        error_items = document.getElementsByClassName("password-dont-match")
        Array.from(error_items).forEach(error => error.remove());
    }
    if (password.value != conf_password.value &&
        document.getElementsByClassName("password-dont-match").length < 1 &&
        conf_password.value.length != 0
    ) {
        let new_list = document.createElement("li");
        new_list.classList.add("password-dont-match", "error-child");
        new_list.textContent = "Password doesn't match!";
        error_list.appendChild(new_list);
    }
    if (
        password.value == "" &&
        document.getElementsByClassName("error-list-element").length < 1
    ) {
        let new_list = document.createElement("li");
        new_list.classList.add("error-list-element", "error-child");
        new_list.textContent = "Password can't be empty!";
        error_list.appendChild(new_list);
    }
    if (document.getElementsByClassName("error-child").length != 0) {
        error_validator.style.display = "block"
    } else {
        error_validator.style.display = "none"
    }

})

conf_password.addEventListener("input", () => {
    if (
        password.value == "" &&
        document.getElementsByClassName("error-list-element").length < 1
    ) {
        let new_list = document.createElement("li");
        new_list.classList.add("error-list-element", "error-child");
        new_list.textContent = "Password can't be empty!";
        error_list.appendChild(new_list);
    }
    if (password.value.length != 0) {
        error_items = document.getElementsByClassName("error-list-element")
        Array.from(error_items).forEach(error => error.remove());
    }
    if (conf_password.value == "" && document.getElementsByClassName("error-list-element").length < 1) {
        let new_list = document.createElement("li");
        new_list.classList.add("error-list-element", "error-child");
        new_list.textContent = "Confirm assword can't be empty!";
        error_list.appendChild(new_list);
    }
    if (password.value == conf_password.value) {
        error_items = document.getElementsByClassName("password-dont-match")
        Array.from(error_items).forEach(error => error.remove());
    }
    if (password.value != conf_password.value &&
        document.getElementsByClassName("password-dont-match").length < 1 &&
        password.value.length != 0
    ) {
        let new_list = document.createElement("li");
        new_list.classList.add("password-dont-match", "error-child");
        new_list.textContent = "Password doesn't match!";
        error_list.appendChild(new_list);
    }
    if (document.getElementsByClassName("error-child").length != 0) {
        error_validator.style.display = "block"
    } else {
        error_validator.style.display = "none"
    }

});
// Toggle Password Visibility 

document.querySelectorAll('.toggle-password').forEach(toggle => {
    const wrapper = toggle.closest('.password-wrapper');
    const input = wrapper.querySelector('.password-input');
    const show = wrapper.querySelector('.icon-show');
    const hide = wrapper.querySelector('.icon-hide');

    // initialize icons
    show.style.display = 'inline';
    hide.style.display = 'none';

    toggle.addEventListener('change', () => {
        const visible = toggle.checked;
        input.type = visible ? 'text' : 'password';
        show.style.display = visible ? 'none' : 'inline';
        hide.style.display = visible ? 'inline' : 'none';
    });
});

