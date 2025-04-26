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
