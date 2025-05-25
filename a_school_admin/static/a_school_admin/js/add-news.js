const photoInput = document.getElementById('photo');
const preview = document.getElementById('preview');

photoInput.addEventListener('change', () => {
    const file = photoInput.files[0];
    if (!file) return preview.style.backgroundImage = '';
    const url = URL.createObjectURL(file);
    preview.style.backgroundImage = `url(${url})`;
});

document.getElementById('newsForm').addEventListener('submit', e => {
    if (!photoInput.files.length) {
        e.preventDefault();
        alert('Please select a photo');
    }
});

