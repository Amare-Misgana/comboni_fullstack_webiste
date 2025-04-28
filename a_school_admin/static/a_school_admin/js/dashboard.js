const nav = document.querySelector("nav");
const modeToggle = document.querySelector(".mode-toggle");
const searchIcon = document.querySelector(".search-box .uil-search");
const sidebarOpen = document.querySelector(".sidebar-toggle");
const sidebarClose = document.querySelector(".uil-bars"); // This seems incorrect based on common patterns, sidebarOpen is likely the icon that *opens* or *toggles*. Let's assume sidebarOpen is the toggle.

let getMode = localStorage.getItem("mode");
if (getMode && getMode === "dark") {
  document.body.classList.add("dark");
}

// Toggle sidebar
sidebarOpen.addEventListener("click", () => {
  nav.classList.toggle("close");
});

// This search icon toggle is commented out in many examples using this CSS,
// but I'll include it in case you need it later.
// searchIcon.addEventListener("click" , () =>{
//     nav.classList.remove("close"); // Assumes clicking search opens sidebar
// })

// Toggle dark mode
modeToggle.addEventListener("click", () => {
  modeToggle.classList.toggle("active");
  document.body.classList.toggle("dark");

  // Save dark mode preference to localStorage
  if (document.body.classList.contains("dark")) {
    localStorage.setItem("mode", "dark");
  } else {
    localStorage.setItem("mode", "light");
  }
});



