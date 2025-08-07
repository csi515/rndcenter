/**
 * 공통 API 호출 관련 JavaScript 함수들
 */

// API 기본 설정
const API_CONFIG = {
    baseURL: '',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
};

/**
 * API 요청 기본 함수
 * @param {string} url - 요청 URL
 * @param {Object} options - 요청 옵션
 * @returns {Promise} API 응답
 */
async function apiRequest(url, options = {}) {
    const config = {
        ...API_CONFIG,
        ...options,
        headers: {
            ...API_CONFIG.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

/**
 * GET 요청
 * @param {string} url - 요청 URL
 * @param {Object} params - 쿼리 파라미터
 * @returns {Promise} API 응답
 */
async function apiGet(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    
    return apiRequest(fullUrl, {
        method: 'GET'
    });
}

/**
 * POST 요청
 * @param {string} url - 요청 URL
 * @param {Object} data - 요청 데이터
 * @returns {Promise} API 응답
 */
async function apiPost(url, data = {}) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * PUT 요청
 * @param {string} url - 요청 URL
 * @param {Object} data - 요청 데이터
 * @returns {Promise} API 응답
 */
async function apiPut(url, data = {}) {
    return apiRequest(url, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * DELETE 요청
 * @param {string} url - 요청 URL
 * @returns {Promise} API 응답
 */
async function apiDelete(url) {
    return apiRequest(url, {
        method: 'DELETE'
    });
}

/**
 * API 응답 처리
 * @param {Object} response - API 응답
 * @param {Function} successCallback - 성공 시 콜백
 * @param {Function} errorCallback - 에러 시 콜백
 */
function handleApiResponse(response, successCallback = null, errorCallback = null) {
    if (response.success) {
        if (successCallback && typeof successCallback === 'function') {
            successCallback(response);
        } else {
            showSuccessMessage(response.message || '성공적으로 처리되었습니다.');
        }
    } else {
        if (errorCallback && typeof errorCallback === 'function') {
            errorCallback(response);
        } else {
            showErrorMessage(response.error || '처리 중 오류가 발생했습니다.');
        }
    }
}

/**
 * 성공 메시지 표시
 * @param {string} message - 메시지
 */
function showSuccessMessage(message) {
    // Bootstrap alert 또는 toast 사용
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        // Toast 메시지 표시
        const toastElement = document.getElementById('successToast');
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            const toastBody = toastElement.querySelector('.toast-body');
            if (toastBody) {
                toastBody.textContent = message;
            }
            toast.show();
        }
    } else {
        alert(message);
    }
}

/**
 * 에러 메시지 표시
 * @param {string} message - 메시지
 */
function showErrorMessage(message) {
    // Bootstrap alert 또는 toast 사용
    if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
        // Toast 메시지 표시
        const toastElement = document.getElementById('errorToast');
        if (toastElement) {
            const toast = new bootstrap.Toast(toastElement);
            const toastBody = toastElement.querySelector('.toast-body');
            if (toastBody) {
                toastBody.textContent = message;
            }
            toast.show();
        }
    } else {
        alert('오류: ' + message);
    }
}

/**
 * 로딩 상태 표시/숨김
 * @param {boolean} show - 표시 여부
 * @param {string} elementId - 로딩 요소 ID
 */
function toggleLoading(show, elementId = 'loadingSpinner') {
    const loadingElement = document.getElementById(elementId);
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

/**
 * 버튼 로딩 상태 설정
 * @param {HTMLElement} button - 버튼 요소
 * @param {boolean} loading - 로딩 상태
 * @param {string} originalText - 원본 텍스트
 */
function setButtonLoading(button, loading, originalText = null) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>처리 중...';
    } else {
        button.disabled = false;
        button.textContent = originalText || button.dataset.originalText || button.textContent;
    }
} 