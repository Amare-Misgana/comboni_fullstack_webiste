document.addEventListener('DOMContentLoaded', function() {
    const checkBtn = document.getElementById('check-existing');
    const classInput = document.getElementById('class-input');
    const duplicateResults = document.getElementById('duplicate-results');
    const duplicateList = document.getElementById('duplicate-list');
    
    checkBtn.addEventListener('click', function() {
        const classNames = classInput.value.split(',').map(name => name.trim()).filter(name => name);
        
        if (classNames.length === 0) {
            alert('Please enter some class names first');
            return;
        }
        
        // Send AJAX request to check existing classes
        fetch('/check-existing-classes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({class_names: classNames})
        })
        .then(response => response.json())
        .then(data => {
            duplicateList.innerHTML = '';
            
            if (data.existing.length > 0) {
                data.existing.forEach(className => {
                    const li = document.createElement('li');
                    li.textContent = className;
                    duplicateList.appendChild(li);
                });
                duplicateResults.classList.remove('hidden');
            } else {
                alert('No existing classes found - all are available!');
                duplicateResults.classList.add('hidden');
            }
        });
    });
});