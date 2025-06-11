// Handle receipt form submission
function showLoading(message = 'Generating receipt...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingMessage = overlay.querySelector('.loading-message');
    loadingMessage.textContent = message;
    overlay.classList.remove('d-none');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('d-none');
}

function showError(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    const form = document.querySelector('form');
    form.insertAdjacentHTML('afterbegin', alertHtml);
}

function handleReceiptFormSubmit(e) {
    e.preventDefault();
    
    // Get form and format info
    const form = e.target;
    const submitButton = document.activeElement;
    const format = submitButton.getAttribute('data-format');
    
    // Don't submit if form is invalid
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    
    // Show loading overlay
    showLoading(`Generating ${format.toUpperCase()} receipt...`);
    
    // Create form data
    const formData = new FormData(form);
    formData.append('format', format);
    
    // Disable submit buttons
    const buttons = form.querySelectorAll('button[type="submit"]');
    buttons.forEach(btn => btn.disabled = true);

    // Submit the form
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(async response => {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            // Handle JSON response (usually errors)
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'An error occurred while generating the receipt.');
            }
            return null;
        }
        
        // Handle file download
        const blob = await response.blob();
        const filename = response.headers.get('content-disposition')
            ?.split('filename=')[1]
            ?.replace(/"/g, '') || `receipt.${format}`;
            
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        showError(error.message);
        console.error('Error:', error);
    })
    .finally(() => {
        // Re-enable buttons and hide loading
        buttons.forEach(btn => btn.disabled = false);
        hideLoading();
    });

    return false;
}
