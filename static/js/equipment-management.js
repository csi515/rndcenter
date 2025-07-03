document.addEventListener('DOMContentLoaded', function() {
    loadEquipmentData();
    updateAddButton();
    // 사용일지 작성 버튼 이벤트 바인딩
    const usageLogBtn = document.getElementById('openUsageLogModalBtn');
    if (usageLogBtn) {
        usageLogBtn.onclick = function() {
            const modal = new bootstrap.Modal(document.getElementById('usageLogModal'));
            modal.show();
        };
    }
});

// 사용일지 작성 버튼 모달 오픈 바인딩 (중복 방지, 항상 적용)
document.addEventListener('DOMContentLoaded', function() {
    const usageLogBtn = document.getElementById('openUsageLogModalBtn');
    if (usageLogBtn) {
        usageLogBtn.onclick = function() {
            const modal = new bootstrap.Modal(document.getElementById('usageLogModal'));
            modal.show();
        };
    }
}); 