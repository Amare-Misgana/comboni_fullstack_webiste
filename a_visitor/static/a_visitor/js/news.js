document.addEventListener("DOMContentLoaded", function () {
  const maxLength = 180;
  document.querySelectorAll(".news-card .description").forEach((el) => {
    if (el.textContent.length > maxLength) {
      el.textContent = el.textContent.slice(0, maxLength) + "...";
    }
  });
});
