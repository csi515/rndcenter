/**
 * 장비 관리 JavaScript 모듈
 */

// 장비 관리 클래스
class EquipmentManager {
    constructor() {
        this.modalId = 'equipmentModal';
        this.formId = 'equipmentForm';
        this.currentEquipmentId = null;
        this.init();
    }
    
    /**
     * 초기화
     */
    init() {
        this.bindEvents();
        this.loadEquipmentData();
    }
    
    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 점검 주기 계산 이벤트
        document.getElementById('equipmentInspectionCycle')?.addEventListener('change', () => this.calculateNextInspectionDate());
        document.getElementById('equipmentLastInspectionDate')?.addEventListener('change', () => this.calculateNextInspectionDate());
        
        // 폼 제출 이벤트
        document.getElementById(this.formId)?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveEquipment();
        });
        
        // 삭제 버튼 이벤트
        document.getElementById('deleteEquipmentBtn')?.addEventListener('click', () => this.deleteEquipment());
        
        // 테이블 내 버튼 이벤트들
        this.bindTableEvents();
    }
    
    /**
     * 테이블 내 버튼 이벤트 바인딩
     */
    bindTableEvents() {
        // 수정 버튼 이벤트
        document.querySelectorAll('.edit-equipment-btn').forEach(btn => {
            btn.onclick = () => {
                const id = btn.getAttribute('data-id');
                const equipment = JSON.parse(btn.getAttribute('data-equipment'));
                this.editEquipment(id, equipment);
            };
        });

        // 삭제 버튼 이벤트 (테이블 내)
        document.querySelectorAll('.delete-equipment-btn').forEach(btn => {
            btn.onclick = () => {
                const id = btn.getAttribute('data-id');
                const name = btn.getAttribute('data-name');
                this.confirmDelete(id, name);
            };
        });
    }
    
    /**
     * 장비 데이터 로드
     */
    async loadEquipmentData() {
        try {
            toggleLoading(true);
            const response = await apiGet('/equipment/api/equipment');
            
            if (response.success && response.data) {
                this.renderEquipmentTable(response.data);
            } else {
                console.error('장비 데이터 로드 실패:', response.error || '데이터 없음');
                this.renderEquipmentTable([]);
            }
        } catch (error) {
            console.error('장비 데이터 로드 중 오류:', error);
            this.renderEquipmentTable([]);
        } finally {
            toggleLoading(false);
        }
    }
    
    /**
     * 장비 테이블 렌더링
     */
    renderEquipmentTable(equipment) {
        const tbody = document.getElementById('equipmentTableBody');
        if (!tbody) return;
        
        let html = '';
        
        if (equipment.length === 0) {
            html = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="fas fa-box-open fa-2x mb-2"></i><br>
                    등록된 장비가 없습니다.<br>
                    <button class="btn btn-primary mt-2" onclick="equipmentManager.addEquipment()">
                        <i class="fas fa-plus me-1"></i>첫 번째 장비 등록하기
                    </button>
                </td>
            </tr>`;
        } else {
            equipment.forEach(eq => {
                const inspectionStatusClass = this.getInspectionStatusClass(eq.inspection_status);
                const inspectionStatusText = eq.inspection_status || '정상';
                const nextInspectionDate = eq.next_inspection_date ? 
                    new Date(eq.next_inspection_date).toLocaleDateString('ko-KR') : '-';
                
                html += `
                <tr class="${inspectionStatusClass}">
                    <td>${eq.equipment_id || '-'}</td>
                    <td>${(typeof eq.asset_number !== 'undefined' && eq.asset_number && eq.asset_number.trim()) ? eq.asset_number : '-'}</td>
                    <td><a href="#" onclick="equipmentManager.viewEquipmentDetail(${eq.id})" class="text-primary">${eq.name}</a></td>
                    <td>${eq.model || '-'}</td>
                    <td>${eq.manufacturer || '-'}</td>
                    <td>${eq.location || '-'}</td>
                    <td>${eq.manager || '-'}</td>
                    <td>
                        <span class="status-badge status-${eq.status ? eq.status.replace(/\s+/g, '') : 'unknown'}">${eq.status || '알 수 없음'}</span>
                    </td>
                    <td>
                        <span class="badge ${this.getInspectionBadgeClass(eq.inspection_status)}">${inspectionStatusText}</span>
                    </td>
                    <td>${nextInspectionDate}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="equipmentManager.editEquipment(${eq.id}, ${JSON.stringify(eq).replace(/"/g, '&quot;')})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="equipmentManager.confirmDelete(${eq.id}, '${eq.name}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
            });
        }
        
        tbody.innerHTML = html;
    }
    
    /**
     * 장비 추가 모달 열기
     */
    addEquipment() {
        this.currentEquipmentId = null;
        
        // 모달 초기화
        setModalTitle(this.modalId, '장비 추가');
        resetModal(this.modalId, () => {
            // 기본값 설정
            document.getElementById('equipmentInspectionCycle').value = '365';
            document.getElementById('equipmentNextInspectionDate').value = '';
            
            // 관리번호 자동 생성
            const nextId = 'EQ' + String(Date.now()).slice(-6);
            document.getElementById('equipmentId').value = nextId;
        });
        
        setModalButtonText(this.modalId, 'equipmentSubmitBtn', '추가');
        toggleModalButton(this.modalId, 'deleteEquipmentBtn', false);
        
        openModal(this.modalId);
    }
    
    /**
     * 장비 수정 모달 열기
     */
    editEquipment(id, equipment) {
        this.currentEquipmentId = id;
        
        // 모달 초기화
        setModalTitle(this.modalId, '장비 수정');
        setModalButtonText(this.modalId, 'equipmentSubmitBtn', '수정');
        toggleModalButton(this.modalId, 'deleteEquipmentBtn', true);
        
        // 데이터 채우기
        fillFormData(this.modalId, {
            equipment_id: id,
            name: equipment.name || '',
            model: equipment.model || '',
            manufacturer: equipment.manufacturer || '',
            location: equipment.location || '',
            manager: equipment.manager || '',
            status: equipment.status || '사용가능',
            purchase_date: equipment.purchase_date || '',
            maintenance_date: equipment.maintenance_date || '',
            inspection_cycle_days: equipment.inspection_cycle_days || 365,
            last_inspection_date: equipment.last_inspection_date || '',
            next_inspection_date: equipment.next_inspection_date || '',
            notes: equipment.notes || ''
        });
        
        openModal(this.modalId);
    }
    
    /**
     * 장비 저장 (추가/수정)
     */
    async saveEquipment() {
        const form = document.getElementById(this.formId);
        if (!form) return;
        
        const formData = getFormData(form);
        const submitBtn = document.getElementById('equipmentSubmitBtn');
        
        try {
            setButtonLoading(submitBtn, true);
            
            let response;
            if (this.currentEquipmentId) {
                // 수정
                response = await apiPost(`/equipment/api/equipment/${this.currentEquipmentId}/update`, formData);
            } else {
                // 추가
                response = await apiPost('/equipment/api/equipment/add', formData);
            }
            
            handleApiResponse(response, () => {
                closeModal(this.modalId);
                this.loadEquipmentData();
            });
            
        } catch (error) {
            console.error('저장 중 오류:', error);
            showErrorMessage('저장 중 오류가 발생했습니다.');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    }
    
    /**
     * 장비 삭제 확인
     */
    confirmDelete(id, name) {
        if (confirm(`정말로 "${name}" 장비를 삭제하시겠습니까?`)) {
            this.deleteEquipmentById(id);
        }
    }
    
    /**
     * 장비 삭제 (모달 내)
     */
    async deleteEquipment() {
        if (!this.currentEquipmentId) return;
        
        const equipmentName = document.getElementById('equipmentName').value;
        this.confirmDelete(this.currentEquipmentId, equipmentName);
    }
    
    /**
     * 장비 삭제 실행
     */
    async deleteEquipmentById(id) {
        try {
            const response = await apiPost(`/equipment/api/equipment/${id}/delete`);
            
            handleApiResponse(response, () => {
                closeModal(this.modalId);
                this.loadEquipmentData();
            });
            
        } catch (error) {
            console.error('삭제 중 오류:', error);
            showErrorMessage('삭제 중 오류가 발생했습니다.');
        }
    }
    
    /**
     * 다음 점검일 자동 계산
     */
    calculateNextInspectionDate() {
        const cycleDays = parseInt(document.getElementById('equipmentInspectionCycle').value) || 365;
        const lastInspectionDate = document.getElementById('equipmentLastInspectionDate').value;
        
        if (lastInspectionDate) {
            const lastDate = new Date(lastInspectionDate);
            const nextDate = new Date(lastDate);
            nextDate.setDate(lastDate.getDate() + cycleDays);
            
            const nextDateStr = nextDate.toISOString().split('T')[0];
            document.getElementById('equipmentNextInspectionDate').value = nextDateStr;
        } else {
            document.getElementById('equipmentNextInspectionDate').value = '';
        }
    }
    
    /**
     * 점검 상태에 따른 행 색상 클래스 반환
     */
    getInspectionStatusClass(status) {
        switch(status) {
            case '점검지연': return 'table-danger';
            case '점검필요': return 'table-warning';
            case '정상':
            default: return '';
        }
    }
    
    /**
     * 점검 상태에 따른 배지 클래스 반환
     */
    getInspectionBadgeClass(status) {
        switch(status) {
            case '점검지연': return 'bg-danger';
            case '점검필요': return 'bg-warning text-dark';
            case '정상':
            default: return 'bg-success';
        }
    }
}

// 전역 인스턴스 생성
let equipmentManager;

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    equipmentManager = new EquipmentManager();
}); 