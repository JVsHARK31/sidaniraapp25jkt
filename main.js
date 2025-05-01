/**
 * SIDANIRA SMPN 25 
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Set active nav item based on current page
    setActiveNavItem();
    
    // Setup password toggle if on login page
    setupPasswordToggle();
    
    // Initialize any tooltips
    initTooltips();
    
    // Setup confirmation dialogs
    setupConfirmationDialogs();
});

/**
 * Set active navigation item based on current page URL
 */
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        }
    });
}

/**
 * Setup password toggle functionality on login page
 */
function setupPasswordToggle() {
    const toggleBtn = document.getElementById('togglePassword');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const passwordInput = document.getElementById('password');
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup confirmation dialogs for dangerous actions
 */
function setupConfirmationDialogs() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Apakah Anda yakin?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Format a number for display
 * @param {number} number - The number to format
 * @returns {string} - Formatted number
 */
function formatNumber(number) {
    return new Intl.NumberFormat('id-ID').format(number);
}

/**
 * Format a date for display
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted date
 */
function formatDate(date) {
    if (!date) return '';
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('id-ID', options);
} 