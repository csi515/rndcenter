// Main JavaScript file for R&D Center Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeSidebar();
    initializeClock();
    initializeTooltips();
    initializeDataTables();
    initializeFormValidation();
    initializeNotifications();
    setActiveMenuItem();
});

// Sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            wrapper.classList.toggle('toggled');
            
            // Save sidebar state to localStorage
            const isToggled = wrapper.classList.contains('toggled');
            localStorage.setItem('sidebarToggled', isToggled);
        });
    }
    
    // Restore sidebar state from localStorage
    const sidebarToggled = localStorage.getItem('sidebarToggled');
    if (sidebarToggled === 'true') {
        wrapper.classList.add('toggled');
    }
    
    // Handle dropdown menus in sidebar
    const dropdownToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const target = document.querySelector(this.dataset.bsTarget);
            if (target) {
                // Close other open dropdowns
                dropdownToggles.forEach(otherToggle => {
                    if (otherToggle !== this) {
                        const otherTarget = document.querySelector(otherToggle.dataset.bsTarget);
                        if (otherTarget && otherTarget.classList.contains('show')) {
                            otherTarget.classList.remove('show');
                        }
                    }
                });
            }
        });
    });
}

// Real-time clock
function initializeClock() {
    const clockElement = document.getElementById('currentTime');
    
    if (clockElement) {
        function updateClock() {
            const now = new Date();
            const timeString = now.toLocaleString('ko-KR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
            });
            clockElement.textContent = timeString;
        }
        
        // Update immediately and then every second
        updateClock();
        setInterval(updateClock, 1000);
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Enhanced data tables functionality
function initializeDataTables() {
    // Add sorting functionality to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('button')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
}

// Table sorting function
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('th')[columnIndex];
    
    // Determine sort direction
    const isAscending = !header.classList.contains('sort-desc');
    
    // Clear all sort classes
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Add appropriate sort class
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numbers
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        } else {
            return isAscending ? 
                aValue.localeCompare(bValue, 'ko-KR') : 
                bValue.localeCompare(aValue, 'ko-KR');
        }
    });
    
    // Reattach sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for specific fields
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', validateEmail);
    });
    
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('blur', validatePhone);
    });
}

// Email validation
function validateEmail(event) {
    const input = event.target;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (input.value && !emailRegex.test(input.value)) {
        input.setCustomValidity('올바른 이메일 형식을 입력해주세요.');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (input.value) input.classList.add('is-valid');
    }
}

// Phone validation
function validatePhone(event) {
    const input = event.target;
    const phoneRegex = /^(\d{2,3}-\d{3,4}-\d{4}|\d{10,11})$/;
    
    if (input.value && !phoneRegex.test(input.value.replace(/\s/g, ''))) {
        input.setCustomValidity('올바른 전화번호 형식을 입력해주세요. (예: 010-1234-5678)');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (input.value) input.classList.add('is-valid');
    }
}

// Notification system
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 300);
                }
            }, 5000);
        }
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of main content
    const mainContent = document.querySelector('.container-fluid');
    if (mainContent) {
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.style.opacity = '0';
                setTimeout(() => alertContainer.remove(), 300);
            }
        }, 5000);
    }
}

// AJAX form submission helper
function submitForm(formElement, successCallback, errorCallback) {
    const formData = new FormData(formElement);
    
    fetch(formElement.action, {
        method: formElement.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json().catch(() => ({ success: true }));
        } else {
            throw new Error('Network response was not ok');
        }
    })
    .then(data => {
        if (data.success) {
            if (successCallback) successCallback(data);
            showNotification(data.message || '작업이 성공적으로 완료되었습니다.', 'success');
        } else {
            if (errorCallback) errorCallback(data);
            showNotification(data.message || '작업 중 오류가 발생했습니다.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) errorCallback({ error: error.message });
        showNotification('작업 중 오류가 발생했습니다.', 'danger');
    });
}

// CSV export functionality
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    const csvContent = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => {
            let text = cell.textContent.trim();
            // Remove action buttons content
            if (cell.querySelector('.btn')) {
                text = '';
            }
            // Escape quotes and wrap in quotes if contains comma
            if (text.includes(',') || text.includes('"')) {
                text = '"' + text.replace(/"/g, '""') + '"';
            }
            return text;
        }).join(',');
    }).join('\n');
    
    // Create and download file
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename + '.csv';
    link.click();
    URL.revokeObjectURL(link.href);
}

// Print functionality
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>인쇄</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                @media print {
                    .btn { display: none !important; }
                    .modal-footer { display: none !important; }
                }
            </style>
        </head>
        <body>
            ${element.innerHTML}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('ko-KR');
}

function formatNumber(number) {
    return new Intl.NumberFormat('ko-KR').format(number);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: 'KRW'
    }).format(amount);
}

// Debounce function for search inputs
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

// 현재 페이지에 맞는 메뉴 아이템 활성화
function setActiveMenuItem() {
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.list-group-item[href]');
    
    // 모든 메뉴 아이템에서 active 클래스 제거
    menuItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // 현재 경로와 일치하는 메뉴 아이템 찾기
    let activeItem = null;
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath) {
            activeItem = item;
        }
    });
    
    // 활성 메뉴 아이템 설정
    if (activeItem) {
        activeItem.classList.add('active');
        
        // 상위 아코디언 메뉴가 있다면 열기
        const parentCollapse = activeItem.closest('.collapse');
        if (parentCollapse) {
            parentCollapse.classList.add('show');
            
            // 아코디언 토글 버튼의 aria-expanded 속성 설정
            const toggleButton = document.querySelector(`[data-bs-target="#${parentCollapse.id}"]`);
            if (toggleButton) {
                toggleButton.setAttribute('aria-expanded', 'true');
            }
        }
    }
}

// Enhanced search functionality
function initializeSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    const debouncedSearch = debounce(function(searchTerm) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm.toLowerCase())) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        // Update row count
        const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
        updateTableInfo(table, visibleRows.length, rows.length);
    }, 300);
    
    searchInput.addEventListener('input', function() {
        debouncedSearch(this.value);
    });
}

// Update table information
function updateTableInfo(table, visibleCount, totalCount) {
    let info = table.parentElement.querySelector('.table-info');
    if (!info) {
        info = document.createElement('div');
        info.className = 'table-info text-muted small mt-2';
        table.parentElement.appendChild(info);
    }
    
    if (visibleCount !== totalCount) {
        info.textContent = `총 ${totalCount}개 중 ${visibleCount}개 표시`;
    } else {
        info.textContent = `총 ${totalCount}개`;
    }
}

// Local storage helpers
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
    }
}

function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Failed to load from localStorage:', e);
        return null;
    }
}

// Modal utilities
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        new bootstrap.Modal(modal).show();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

// Progress indicator
function showProgress() {
    const progressHtml = `
        <div class="progress-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">로딩 중...</span>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', progressHtml);
}

function hideProgress() {
    const overlay = document.querySelector('.progress-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    showNotification('예기치 않은 오류가 발생했습니다.', 'danger');
});

// Expose global functions
window.RDCenter = {
    showNotification,
    submitForm,
    exportTableToCSV,
    printElement,
    openModal,
    closeModal,
    showProgress,
    hideProgress,
    formatDate,
    formatNumber,
    formatCurrency,
    saveToLocalStorage,
    loadFromLocalStorage
};
