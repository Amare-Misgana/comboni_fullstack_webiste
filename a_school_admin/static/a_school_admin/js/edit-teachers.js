document.getElementById('teacher-profile').addEventListener('change', function (e) {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (ev) => {
        document.getElementById('teacher-preview').src = ev.target.result
    }
    reader.readAsDataURL(file)
})