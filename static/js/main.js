// Validación en tiempo real
document.querySelector('form').addEventListener('submit', function(e) {
    const inputs = this.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('is-invalid');
        }
    });
    
    if (!isValid) e.preventDefault();
});