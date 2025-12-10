// Resume Analyzer Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.getElementById('spinner');
    const statusMessage = document.getElementById('statusMessage');

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
            fileName.style.display = 'block';
        } else {
            fileName.style.display = 'none';
        }
    });

    // Form submit handler
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showStatus('Please select a ZIP file to upload.', 'error');
            return;
        }

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.zip')) {
            showStatus('Please select a valid ZIP file.', 'error');
            return;
        }

        // Start processing
        setLoadingState(true);
        showStatus('Processing resumes... This may take a few moments.', 'info');

        try {
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);

            // Make API request
            const response = await fetch('/api/download-csv', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                // Handle error response
                let errorMessage = 'An error occurred while processing the file.';
                
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    // If response is not JSON, use status text
                    errorMessage = response.statusText || errorMessage;
                }
                
                throw new Error(errorMessage);
            }

            // Get the CSV blob
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume_report.csv';
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success message
            showStatus('CSV report generated and downloaded successfully!', 'success');
            
            // Reset form
            uploadForm.reset();
            fileName.style.display = 'none';

        } catch (error) {
            console.error('Error:', error);
            showStatus(error.message, 'error');
        } finally {
            setLoadingState(false);
        }
    });

    // Helper function to set loading state
    function setLoadingState(isLoading) {
        submitBtn.disabled = isLoading;
        
        if (isLoading) {
            btnText.textContent = 'Processing...';
            spinner.classList.add('show');
        } else {
            btnText.textContent = 'Analyze & Download CSV';
            spinner.classList.remove('show');
        }
    }

    // Helper function to show status messages
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message show ${type}`;
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                statusMessage.classList.remove('show');
            }, 5000);
        }
    }

    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Drag and drop functionality
    const fileLabel = document.querySelector('.file-label');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        fileLabel.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    fileLabel.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        fileLabel.style.borderColor = '#667eea';
        fileLabel.style.backgroundColor = '#e9ecef';
    }

    function unhighlight(e) {
        fileLabel.style.borderColor = '#dee2e6';
        fileLabel.style.backgroundColor = '#f8f9fa';
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
});