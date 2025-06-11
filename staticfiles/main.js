// Receipt form submission handling
function handleReceiptFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    // Get which button was clicked (PDF or IMG)
    const submitButton = document.activeElement;
    const format = submitButton.getAttribute('data-format');
    formData.append('format', format);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })    .then(response => {        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'An error occurred');
                }
            });
        }
        
        // If not JSON, it's a file download
        return response.blob().then(blob => {
            // Create and trigger download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // Get filename from Content-Disposition header if available
            const disposition = response.headers.get('content-disposition');
            let filename;
            if (disposition && disposition.indexOf('filename=') !== -1) {
                filename = disposition.split('filename=')[1].replace(/"/g, '');
            } else {
                filename = `receipt.${format === 'pdf' ? 'pdf' : 'png'}`;
            }
            a.download = filename;
            
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Show success message
            const successDiv = document.createElement('div');
            successDiv.className = 'alert alert-success';
            successDiv.textContent = `Receipt generated successfully as ${format.toUpperCase()}!`;
            form.querySelector('.form-actions').appendChild(successDiv);
            
            // Remove success message after 5 seconds
            setTimeout(() => {
                successDiv.remove();
            }, 5000);
        });
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = error.message || 'A network error occurred.';
        form.querySelector('.form-actions').appendChild(errorDiv);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = 'A network error occurred.';
        form.querySelector('.form-actions').appendChild(errorDiv);
    });
}
