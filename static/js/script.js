// JavaScript for Arabic Hospitality Request System

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
    setupFormValidation();
    setupDateValidation();
    setupFileUpload();
});

// Initialize form functionality
function initializeForm() {
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fromDate').setAttribute('min', today);
    document.getElementById('toDate').setAttribute('min', today);
    
    // Setup date change handlers
    document.getElementById('fromDate').addEventListener('change', updateMinToDate);
    document.getElementById('toDate').addEventListener('change', validateDateRange);
    
    // Setup phone number formatting
    const telegramInput = document.getElementById('telegram');
    telegramInput.addEventListener('input', formatPhoneNumber);
    telegramInput.addEventListener('blur', validatePhoneNumber);
    
    // Setup form submission
    document.getElementById('hospitalityForm').addEventListener('submit', handleFormSubmission);
}

// Add new booking input
function addBooking() {
    const container = document.getElementById('bookingContainer');
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="text" class="form-control" name="booking" placeholder="رقم الحجز">
        <button type="button" class="btn btn-outline-danger" onclick="removeBooking(this)">
            <i class="fas fa-minus"></i>
        </button>
    `;
    container.appendChild(div);
    
    // Focus on the new input
    div.querySelector('input').focus();
}

// Remove booking input
function removeBooking(button) {
    const container = document.getElementById('bookingContainer');
    if (container.children.length > 1) {
        button.parentElement.remove();
    } else {
        // Clear the input instead of removing if it's the last one
        button.parentElement.querySelector('input').value = '';
    }
}

// Add new guest input
function addGuest() {
    const container = document.getElementById('guestContainer');
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="text" class="form-control" name="guest" placeholder="اسم الضيف">
        <button type="button" class="btn btn-outline-danger" onclick="removeGuest(this)">
            <i class="fas fa-minus"></i>
        </button>
    `;
    container.appendChild(div);
    
    // Focus on the new input
    div.querySelector('input').focus();
}

// Remove guest input
function removeGuest(button) {
    const container = document.getElementById('guestContainer');
    if (container.children.length > 1) {
        button.parentElement.remove();
    } else {
        // Clear the input instead of removing if it's the last one
        button.parentElement.querySelector('input').value = '';
    }
}

// Update minimum to-date based on from-date
function updateMinToDate() {
    const fromDate = document.getElementById('fromDate').value;
    const toDateInput = document.getElementById('toDate');
    
    if (fromDate) {
        toDateInput.setAttribute('min', fromDate);
        
        // If to-date is before from-date, clear it
        if (toDateInput.value && toDateInput.value < fromDate) {
            toDateInput.value = '';
            showToast('تاريخ المغادرة يجب أن يكون بعد تاريخ الوصول', 'warning');
        }
    }
}

// Setup date validation
function setupDateValidation() {
    const fromDateInput = document.getElementById('fromDate');
    const toDateInput = document.getElementById('toDate');
    
    // Add validation event listeners
    fromDateInput.addEventListener('change', updateMinToDate);
    toDateInput.addEventListener('change', validateDateRange);
}

// Validate date range
function validateDateRange() {
    const fromDate = document.getElementById('fromDate').value;
    const toDate = document.getElementById('toDate').value;
    
    if (fromDate && toDate) {
        const from = new Date(fromDate);
        const to = new Date(toDate);
        
        if (to <= from) {
            document.getElementById('toDate').value = '';
            showToast('تاريخ المغادرة يجب أن يكون بعد تاريخ الوصول', 'warning');
            return false;
        }
        
        // Check if the duration is reasonable (e.g., not more than 30 days)
        const diffTime = Math.abs(to - from);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays > 30) {
            showToast('مدة الإقامة لا يمكن أن تزيد عن 30 يوماً', 'warning');
            return false;
        }
    }
    
    return true;
}

// Format phone number input
function formatPhoneNumber(event) {
    let value = event.target.value.replace(/\D/g, ''); // Remove non-digits
    
    // Ensure it starts with 01
    if (value.length > 0 && !value.startsWith('01')) {
        if (value.startsWith('1')) {
            value = '0' + value;
        } else if (value.startsWith('0') && value[1] !== '1') {
            value = '01' + value.substring(1);
        } else {
            value = '01' + value;
        }
    }
    
    // Limit length to 11 digits
    if (value.length > 11) {
        value = value.substring(0, 11);
    }
    
    event.target.value = value;
}

// Validate Egyptian phone number
function validatePhoneNumber(event) {
    const value = event.target.value;
    const pattern = /^01[0-9]{8,9}$/;
    
    if (value && !pattern.test(value)) {
        event.target.setCustomValidity('رقم التليجرام غير صحيح. يجب أن يبدأ بـ 01 ويتكون من 10-11 رقم');
        event.target.classList.add('is-invalid');
        showToast('رقم التليجرام غير صحيح', 'error');
    } else {
        event.target.setCustomValidity('');
        event.target.classList.remove('is-invalid');
        if (value) {
            event.target.classList.add('is-valid');
        }
    }
}

// Setup form validation
function setupFormValidation() {
    const form = document.getElementById('hospitalityForm');
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

// Validate individual field
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
    } else if (value) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    }
}

// Clear field error state
function clearFieldError(event) {
    const field = event.target;
    if (field.classList.contains('is-invalid')) {
        field.classList.remove('is-invalid');
    }
}

// Setup file upload handling
function setupFileUpload() {
    const fileInput = document.getElementById('file');
    fileInput.addEventListener('change', handleFileSelect);
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (file) {
        // Check file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB in bytes
        if (file.size > maxSize) {
            event.target.value = '';
            showToast('حجم الملف كبير جداً. الحد الأقصى 10 ميجابايت', 'error');
            return;
        }
        
        // Check file type
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            event.target.value = '';
            showToast('نوع الملف غير مدعوم. الأنواع المسموحة: PDF, Word, صور', 'error');
            return;
        }
        
        // Show file info
        showToast(`تم اختيار الملف: ${file.name}`, 'success');
    }
}

// Handle form submission
function handleFormSubmission(event) {
    event.preventDefault();
    
    // Validate all required fields
    const form = event.target;
    const requiredFields = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Validate date range
    if (!validateDateRange()) {
        isValid = false;
    }
    
    // Validate phone number
    const telegramInput = document.getElementById('telegram');
    const phonePattern = /^01[0-9]{8,9}$/;
    if (!phonePattern.test(telegramInput.value)) {
        telegramInput.classList.add('is-invalid');
        isValid = false;
    }
    
    if (!isValid) {
        showToast('يرجى التأكد من ملء جميع الحقول المطلوبة بشكل صحيح', 'error');
        return;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري الإرسال...';
    submitButton.disabled = true;
    submitButton.classList.add('btn-loading');
    
    // Submit the form
    setTimeout(() => {
        form.submit();
    }, 500);
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'warning'} toast-notification`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    const icon = type === 'error' ? 'exclamation-triangle' : 
                 type === 'success' ? 'check-circle' : 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .toast-notification {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-radius: 10px;
    }
`;
document.head.appendChild(style);

// Form auto-save functionality (optional)
function setupAutoSave() {
    const form = document.getElementById('hospitalityForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', debounce(saveFormData, 1000));
    });
    
    // Load saved data on page load
    loadFormData();
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Save form data to localStorage
function saveFormData() {
    const form = document.getElementById('hospitalityForm');
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    localStorage.setItem('hospitalityFormData', JSON.stringify(data));
}

// Load form data from localStorage
function loadFormData() {
    const savedData = localStorage.getItem('hospitalityFormData');
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            const form = document.getElementById('hospitalityForm');
            
            Object.keys(data).forEach(key => {
                const elements = form.querySelectorAll(`[name="${key}"]`);
                if (elements.length > 0) {
                    if (Array.isArray(data[key])) {
                        elements.forEach((el, index) => {
                            if (data[key][index]) {
                                el.value = data[key][index];
                            }
                        });
                    } else {
                        elements[0].value = data[key];
                    }
                }
            });
        } catch (e) {
            console.error('Error loading form data:', e);
        }
    }
}

// Clear saved form data
function clearSavedData() {
    localStorage.removeItem('hospitalityFormData');
}

// Initialize auto-save if needed
// Uncomment the line below to enable auto-save functionality
// setupAutoSave();
