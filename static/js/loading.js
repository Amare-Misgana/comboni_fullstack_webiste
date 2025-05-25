document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('loading-overlay');
    const forms = document.querySelectorAll('form.load');

    forms.forEach(form => {
        form.addEventListener('submit', e => {
            if (!form.checkValidity()) return;

            document.documentElement.classList.add('loading-active');
            overlay?.classList.add('active');
        });
    });

    window.addEventListener('pageshow', () => {
        document.documentElement.classList.remove('loading-active');
        overlay?.classList.remove('active');
    });
});