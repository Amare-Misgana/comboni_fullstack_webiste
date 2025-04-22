const toggleBtn = document.querySelector(".menu-toggle");
const navLinks = document.querySelector(".nav_links");
const overlay = document.querySelector(".menu_overlay");
const closeBtn = document.querySelector(".fa-times");

toggleBtn.addEventListener("click", () => {
  navLinks.classList.toggle("active");
  overlay.classList.toggle("active");
});

closeBtn.addEventListener("click", () => {
  navLinks.classList.toggle("active");
  overlay.classList.toggle("active");
});

overlay.addEventListener("click", () => {
  navLinks.classList.remove("active");
  overlay.classList.remove("active");
});
