/**
 * 공통 모달 관련 JavaScript 함수들
 */

// 모달 기본 설정
const MODAL_CONFIG = {
    backdrop: 'static',
    keyboard: false
};

/**
 * 모달 열기
 * @param {string} modalId - 모달 ID
 * @param {Object} options - 추가 옵션
 */
function openModal(modalId, options = {}) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
        console.error(`Modal with ID '${modalId}' not found`);
        return null;
    }
    
    const modal = new bootstrap.Modal(modalElement, { ...MODAL_CONFIG, ...options });
    modal.show();
    return modal;
}

/**
 * 모달 닫기
 * @param {string} modalId - 모달 ID
 */
function closeModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

/**
 * 모달 초기화
 * @param {string} modalId - 모달 ID
 * @param {Function} callback - 초기화 후 실행할 콜백
 */
function resetModal(modalId, callback = null) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const form = modalElement.querySelector('form');
        if (form) {
            form.reset();
        }
        
        // 모든 입력 필드 초기화
        const inputs = modalElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else if (input.type === 'file') {
                input.value = '';
            }
        });
        
        if (callback && typeof callback === 'function') {
            callback();
        }
    }
}

/**
 * 모달 제목 변경
 * @param {string} modalId - 모달 ID
 * @param {string} title - 새로운 제목
 */
function setModalTitle(modalId, title) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const titleElement = modalElement.querySelector('.modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
    }
}

/**
 * 모달 버튼 텍스트 변경
 * @param {string} modalId - 모달 ID
 * @param {string} buttonId - 버튼 ID
 * @param {string} text - 새로운 텍스트
 */
function setModalButtonText(modalId, buttonId, text) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const button = modalElement.querySelector(`#${buttonId}`);
        if (button) {
            button.textContent = text;
        }
    }
}

/**
 * 모달 버튼 표시/숨김
 * @param {string} modalId - 모달 ID
 * @param {string} buttonId - 버튼 ID
 * @param {boolean} show - 표시 여부
 */
function toggleModalButton(modalId, buttonId, show) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const button = modalElement.querySelector(`#${buttonId}`);
        if (button) {
            button.style.display = show ? 'inline-block' : 'none';
        }
    }
}

/**
 * 폼 데이터를 객체로 변환
 * @param {HTMLFormElement} form - 폼 요소
 * @returns {Object} 폼 데이터 객체
 */
function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

/**
 * 객체 데이터를 폼에 채우기
 * @param {string} modalId - 모달 ID
 * @param {Object} data - 데이터 객체
 */
function fillFormData(modalId, data) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement || !data) return;
    
    Object.keys(data).forEach(key => {
        const element = modalElement.querySelector(`[name="${key}"]`) || 
                       modalElement.querySelector(`#${key}`);
        
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = Boolean(data[key]);
            } else if (element.type === 'radio') {
                const radio = modalElement.querySelector(`[name="${key}"][value="${data[key]}"]`);
                if (radio) radio.checked = true;
            } else {
                element.value = data[key] || '';
            }
        }
    });
} 