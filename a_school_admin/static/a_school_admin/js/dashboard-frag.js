class Theme {
  constructor(is_light) {
    this.is_light = is_light;
  }

  getTheme() {
    if (localStorage.getItem("theme") === null) {
      console.log("Theme isn't defined yet!");
    } else {
      this.is_light = localStorage.getItem("theme") === "true";
    }
  }

  setTheme() {
    localStorage.setItem("theme", this.is_light);
  }

  changeTheme() {
    document.querySelector("body").classList.toggle("dark-mode");
    this.is_light = !this.is_light;
    this.setTheme();
  }

  changeByBool() {
    if (this.is_light) {
      document.querySelector("body").classList.remove("dark-mode");
    } else {
      document.querySelector("body").classList.add("dark-mode");
    }
  }

  initialSetUp() {
    this.getTheme();
    this.changeByBool();
    if (!this.is_light) {
      document.querySelector(".theme-toggle").checked = true;
    } else {
      document.querySelector(".theme-toggle").checked = false;
    }
  }
}

// EXCUTE THE THEME

let theme = new Theme(false);

theme.initialSetUp();

document.querySelector(".theme-toggle").addEventListener("change", function () {
  theme.changeTheme();
});

// EXCUTETION END

class SlideBar {
  constructor(is_visible) {
    this.is_visible = is_visible;
  }

  getSlide() {
    if (localStorage.getItem("slide") === null) {
      console.log("Slide isn't defined yet!");
    } else {
      this.is_visible = localStorage.getItem("slide") === "true";
    }
  }

  setSlide() {
    localStorage.setItem("slide", this.is_visible);
  }

  changeSlide() {
    document.querySelector("body").classList.toggle("slide");
    if (this.is_visible) {
      document.querySelector(".layer").style.visibility = "visible";
      document.querySelector(".menu-icon").style.visibility = "hidden";
    } else {
      document.querySelector(".layer").style.visibility = "hidden";
      document.querySelector(".menu-icon").style.visibility = "visible";
    }
    this.is_visible = !this.is_visible;
    this.setSlide();
  }

  changeByBool() {
    if (this.is_visible) {
      document.querySelector("body").classList.add("slide");
      document.querySelector(".layer").style.visibility = "hidden";
    } else {
      document.querySelector(".layer").style.visibility = "visible";
      document.querySelector("body").classList.remove("slide");
    }
  }

  initialSetUp() {
    this.getSlide();
    this.changeByBool();
    if (!this.is_visible) {
      document.querySelector(".menu-icon").style.visibility = "hidden";
    } else {
      document.querySelector(".menu-icon").style.visibility = "visible";
    }
  }
}

// EXCUTE THE SLIDE

let slide = new SlideBar(false);

slide.initialSetUp();

document.querySelector(".menu-icon").addEventListener("click", function () {
  slide.changeSlide();
});
document.querySelector(".layer").addEventListener("click", function () {
  slide.changeSlide();
});
document
  .querySelector(".fa-angle-double-left")
  .addEventListener("click", function () {
    slide.changeSlide();
  });

// EXCUTETION END
