const swiper_feature = new Swiper(".contact-info .swiper", {
  loop: true,
  autoplay: {
    delay: 5000,
    disableOnInteraction: false,
  },
  pagination: {
    el: ".contact-info .swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".contact-info .swiper-button-next",
    prevEl: ".contact-info .swiper-button-prev",
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
