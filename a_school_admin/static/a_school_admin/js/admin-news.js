let max_length = 100
let description = document.querySelectorAll(".description")
description.forEach(descr => {
    if (descr.innerHTML.length > max_length) {
        descr.innerHTML = descr.innerHTML.slice(0, max_length) + "..."
    }
});