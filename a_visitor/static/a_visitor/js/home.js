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

overlay.addEventListener("click", (e) => {
  if (e.target === overlay) {
    navLinks.classList.remove("active");
    overlay.classList.remove("active");
  }
});

const swiper_testimony = new Swiper(".testimonial .swiper", {
  loop: true,
  autoplay: {
    delay: 5000,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".testimonial .swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".testimonial .swiper-button-next",
    prevEl: ".testimonial .swiper-button-prev",
  },
  slidesPerView: 1,
  spaceBetween: 30,
});

const swiper_feature = new Swiper(".feature-section .swiper", {
  loop: true,
  autoplay: {
    delay: 5000,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".feature-section .swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".feature-section .swiper-button-next",
    prevEl: ".feature-section .swiper-button-prev",
  },
  breakpoints: {
    320: {
      slidesPerView: 1,
      spaceBetween: 10,
    },
    640: {
      slidesPerView: 2,
      spaceBetween: 20,
    },
    1024: {
      slidesPerView: 3,
      spaceBetween: 30,
    },
  },
});
