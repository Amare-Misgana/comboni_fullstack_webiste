function handleFileSelect(event) {
  const fileInput = event.target;
  const selectedFile = document.getElementById('selectedFile');
  if (fileInput.files.length > 0) {
    selectedFile.textContent = `Selected file: ${fileInput.files[0].name}`;
  } else {
    selectedFile.textContent = '';
  }
}