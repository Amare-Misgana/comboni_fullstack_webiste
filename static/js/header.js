const toggleBtn = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav_links");
const overlay = document.querySelector(".menu_overlay");
const closeBtn = document.querySelector(".fa-times");

function toggleing() {
  navLinks.classList.toggle("active");
  overlay.classList.toggle("active");
  if (navLinks.classList.contains("active")) {
    document.body.style.overflow = "hidden";
  } else {
    document.body.style.overflow = "";
  }
}

toggleBtn.addEventListener("click", () => {
  toggleing();
});

closeBtn.addEventListener("click", () => {
  toggleing();
});

overlay.addEventListener("click", (e) => {
  if (e.target === overlay) {
    toggleing();
  }
});

