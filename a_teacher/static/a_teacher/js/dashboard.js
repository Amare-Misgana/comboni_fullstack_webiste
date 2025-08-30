const profile_info = document.querySelector(".profile-settings")
const settings_btn = document.getElementById("settings")
const layer_sub = document.querySelector(".sub-layer")
const close_profile = document.getElementById("close-profile")


settings_btn.addEventListener("click", () => {
    profile_info.style.display = "flex"
    layer_sub.style.display = "block"
})

layer_sub.addEventListener("click", () => {
    profile_info.style.display = "none"
    layer_sub.style.display = "none"
})

close_profile.addEventListener("click", () => {
    profile_info.style.display = "none"
    layer_sub.style.display = "none"
})