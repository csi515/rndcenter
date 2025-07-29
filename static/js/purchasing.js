// 구매 관리 JS
let requests = [];
let projectTypes = [];

// Toast 알림
function showToast(msg, type='primary') {
  const toast = document.getElementById('toastMsg');
  toast.className = `toast align-items-center text-bg-${type} border-0`;
  toast.querySelector('.toast-body').textContent = msg;
  new bootstrap.Toast(toast).show();
}

// 총 가격 자동 계산 (모달 폼에 맞게 보완)
function updateTotalPrice() {
  const qtyEl = document.getElementById('purchaseQty');
  const priceEl = document.getElementById('unitPrice');
  const totalEl = document.getElementById('totalPrice');
  
  if (!qtyEl || !priceEl || !totalEl) return;
  
  const qty = Number(qtyEl.value) || 0;
  const price = Number(priceEl.value) || 0;
  // value는 항상 콤마 없는 숫자, 표시용은 placeholder 등에서 처리
  totalEl.value = qty * price;
}

// 총 가격 계산 이벤트 바인딩
function bindTotalPriceEvents() {
  const qtyEl = document.getElementById('purchaseQty');
  const priceEl = document.getElementById('unitPrice');
  
  if (qtyEl && priceEl) {
    // 기존 이벤트 제거 후 다시 바인딩
    qtyEl.removeEventListener('input', updateTotalPrice);
    priceEl.removeEventListener('input', updateTotalPrice);
    
    qtyEl.addEventListener('input', updateTotalPrice);
    priceEl.addEventListener('input', updateTotalPrice);
    
    // 초기 계산
    updateTotalPrice();
  }
}

// 국책과제 종류 드롭다운/필터 동기화
function renderProjectTypeSelect() {
  // 모달 내 드롭다운
  const modalSelect = document.getElementById('projectTypeSelect');
  if (modalSelect) {
    modalSelect.innerHTML = '<option value="">선택하세요</option>';
    projectTypes.forEach(type => {
      modalSelect.innerHTML += `<option value="${type}">${type}</option>`;
    });
  }
  
  // 필터 드롭다운
  const filterSelect = document.getElementById('filterProjectType');
  if (filterSelect) {
    const currentValue = filterSelect.value; // 현재 선택된 값 보존
    filterSelect.innerHTML = '<option value="">국책과제</option>';
    projectTypes.forEach(type => {
      filterSelect.innerHTML += `<option value="${type}">${type}</option>`;
    });
    filterSelect.value = currentValue; // 선택된 값 복원
  }
}

// 국책과제 종류 관리 모달 (테이블 기반)
function renderProjectTypeTable(list) {
  const tbody = document.querySelector('#projectTypeTable tbody');
  tbody.innerHTML = '';
  list.forEach(type => {
    const tr = document.createElement('tr');
    tr.dataset.id = type.id;
    // 기본 셀(수정모드 아님)
    tr.innerHTML = `
      <td><span class="type-label">${type.project_type}</span></td>
      <td class="text-center">
        <button class="btn btn-sm btn-outline-secondary me-1 edit-btn" title="수정"><span>✏️</span></button>
        <button class="btn btn-sm btn-outline-danger delete-btn" title="삭제"><span>🗑</span></button>
      </td>
    `;
    // 수정 버튼
    tr.querySelector('.edit-btn').onclick = function() {
      const td = tr.querySelector('td');
      const oldVal = type.project_type;
      td.innerHTML = `<input type='text' class='form-control form-control-sm edit-input' value='${oldVal}'>`;
      const saveBtn = document.createElement('button');
      saveBtn.className = 'btn btn-sm btn-success ms-1';
      saveBtn.innerHTML = '저장';
      saveBtn.onclick = function() {
        const newVal = td.querySelector('.edit-input').value.trim();
        if(!newVal) return showToast('값을 입력하세요.','warning');
        fetch('/purchasing/project-types/add',{
          method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_type:newVal})
        }).then(r=>r.json()).then(res=>{
          if(res.success) {
            // 기존 값 삭제
            fetch(`/purchasing/project-types/delete/${type.id}`,{method:'POST'}).then(()=>{
              showToast('수정되었습니다.','success');
              loadProjectTypes();
            });
          } else showToast(res.error||'수정 실패','danger');
        });
      };
      td.appendChild(saveBtn);
    };
    // 삭제 버튼
    tr.querySelector('.delete-btn').onclick = function() {
      if(!confirm('정말 삭제하시겠습니까?')) return;
      fetch(`/purchasing/project-types/delete/${type.id}`,{method:'POST'}).then(r=>r.json()).then(res=>{
        if(res.success) { showToast('삭제되었습니다.','success'); loadProjectTypes(); }
        else showToast('삭제 실패','danger');
      });
    };
    tbody.appendChild(tr);
  });
}
function loadProjectTypes() {
  fetch('/purchasing/project-types/list').then(r=>r.json()).then(list=>{
    projectTypes = list.map(x=>x.project_type);
    renderProjectTypeSelect();
    renderProjectTypeTable(list);
  });
}

// 구매 요청 목록 불러오기/필터
function loadRequests(scrollTop) {
  const params = new URLSearchParams();
  if(document.getElementById('filterItem').value) params.append('item', document.getElementById('filterItem').value);
  if(document.getElementById('filterRequester').value) params.append('requester', document.getElementById('filterRequester').value);
  if(document.getElementById('filterProjectType').value) params.append('project_type', document.getElementById('filterProjectType').value);
  fetch('/purchasing/requests/list?'+params.toString()).then(r=>r.json()).then(list=>{
    // 최신 데이터가 항상 최상단에 오도록 정렬
    requests = list.sort((a,b)=> (b.request_date||'').localeCompare(a.request_date||'') || (b.id||'').localeCompare(a.id||''));
    renderTable();
    updateSummary();
    if(scrollTop) {
      const table = document.getElementById('requestTable');
      if(table) table.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
}

// 테이블 렌더링
function renderTable() {
  const tbody = document.querySelector('#requestTable tbody');
  tbody.innerHTML = '';
  // CSV/테이블 컬럼 순서 매핑 (구매여부를 맨 오른쪽으로 이동)
  const columns = [
    'item','spec','item_number','unit','project_type','purchase_qty','unit_price','total_price','note','reason','requester','request_date','purchase_status'
  ];
  requests.forEach(req=>{
    const tr = document.createElement('tr');
    columns.forEach(k=>{
      const td = document.createElement('td');
      if (k === 'purchase_status') {
        // 구매 여부 상태 버튼
        const status = req[k] || '대기';
        let statusClass = 'btn-secondary';
        let statusIcon = '⏳';
        
        if (status === '완료') {
          statusClass = 'btn-success';
          statusIcon = '✅';
        } else if (status === '취소') {
          statusClass = 'btn-danger';
          statusIcon = '❌';
        }
        
        td.innerHTML = `<button class="btn btn-sm ${statusClass}" onclick="togglePurchaseStatus('${req.id}')" title="클릭하여 상태 변경">${statusIcon} ${status}</button>`;
        td.style.textAlign = 'center';
      } else {
        td.textContent = (k==='total_price'||k==='unit_price'||k==='purchase_qty') ? Number(req[k]||0).toLocaleString() : (req[k]||'');
      }
      tr.appendChild(td);
    });
    // 액션 버튼
    const td = document.createElement('td');
    td.innerHTML = `
      <div class="action-btns">
        <button class="btn btn-sm btn-outline-primary me-1" onclick="editRequest('${req.id}')" title="수정"><i class="fas fa-edit"></i></button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteRequest('${req.id}')" title="삭제"><i class="fas fa-trash-alt"></i></button>
      </div>
    `;
    tr.appendChild(td);
    tbody.appendChild(tr);
  });
}

// 요약 정보
function updateSummary() {
  document.getElementById('totalCount').textContent = `총 ${requests.length}건`;
  const sum = requests.reduce((a,b)=>a+Number(b.total_price||0),0);
  document.getElementById('totalPrice').textContent = `총액: ${sum.toLocaleString()}원`;
}

// 품목 행 클릭 시 상세/수정 모달 오픈
function bindInventoryRowClick() {
  document.querySelectorAll('#inventoryTable tbody tr').forEach(tr => {
    tr.onclick = function() {
      const cells = tr.children;
      const id = tr.getAttribute('data-id');
      document.querySelector('#inventoryEditForm [name="id"]').value = id;
      document.querySelector('#inventoryEditForm [name="name"]').value = cells[0].textContent.trim();
      document.querySelector('#inventoryEditForm [name="spec"]').value = cells[1].textContent.trim();
      document.querySelector('#inventoryEditForm [name="item_id"]').value = cells[2].textContent.trim();
      document.querySelector('#inventoryEditForm [name="min_quantity"]').value = cells[3].textContent.trim();
      const modalEl = document.getElementById('inventoryEditModal');
      let modal = bootstrap.Modal.getInstance(modalEl);
      if (!modal) modal = new bootstrap.Modal(modalEl);
      modal.show();
    };
  });
}

function loadInventoryTable() {
  fetch('/inventory/api/list')
    .then(res => res.json())
    .then(list => {
      // 필터 적용
      const nameFilter = document.getElementById('inventoryFilterName').value.trim().toLowerCase();
      const specFilter = document.getElementById('inventoryFilterSpec').value.trim().toLowerCase();
      const idFilter = document.getElementById('inventoryFilterId').value.trim().toLowerCase();
      const filtered = list.filter(item => {
        return (!nameFilter || (item.name||'').toLowerCase().includes(nameFilter)) &&
               (!specFilter || (item.spec||'').toLowerCase().includes(specFilter)) &&
               (!idFilter || (item.item_id||'').toLowerCase().includes(idFilter));
      });
      const tbody = document.querySelector('#inventoryTable tbody');
      tbody.innerHTML = '';
      filtered.forEach(item => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-id', item.id);
        tr.innerHTML = `
          <td>${item.name || ''}</td>
          <td>${item.spec || ''}</td>
          <td>${item.item_id || ''}</td>
          <td>${item.min_quantity || 0}</td>
          <td class="text-center">
            <button class="btn btn-sm btn-outline-primary edit-inv-btn" title="수정"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-outline-danger delete-inv-btn" title="삭제"><i class="fas fa-trash-alt"></i></button>
          </td>
        `;
        tbody.appendChild(tr);
      });
      bindInventoryRowClick();
      document.getElementById('inventoryCountNum').textContent = filtered.length;
      // 수정/삭제 버튼 이벤트 바인딩
      document.querySelectorAll('.edit-inv-btn').forEach((btn, idx) => {
        btn.onclick = function(e) {
          e.stopPropagation();
          const tr = btn.closest('tr');
          tr.click(); // 기존 행 클릭(수정 모달 오픈)
        };
      });
      document.querySelectorAll('.delete-inv-btn').forEach((btn, idx) => {
        btn.onclick = function(e) {
          e.stopPropagation();
          const tr = btn.closest('tr');
          const id = tr.getAttribute('data-id');
          if(!confirm('정말 삭제하시겠습니까?')) return;
          fetch('/inventory/api/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id})
          }).then(res => res.json()).then(result => {
            if(result.success) {
              loadInventoryTable();
              alert('삭제되었습니다.');
            } else {
              alert('삭제 실패: ' + (result.message || '오류'));
            }
          });
        };
      });
    });
}

// 품목 수정
  document.getElementById('saveInventoryBtn').onclick = function(e) {
    e.preventDefault();
    const form = document.getElementById('inventoryEditForm');
    const fd = new FormData(form);
    const data = Object.fromEntries(fd.entries());
    fetch('/inventory/api/update', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    }).then(res => res.json()).then(result => {
      if(result.success) {
        bootstrap.Modal.getInstance(document.getElementById('inventoryEditModal')).hide();
        loadInventoryTable();
        alert('수정되었습니다.');
      } else {
        alert('수정 실패: ' + (result.message || '오류'));
      }
    });
  };
// 품목 삭제
  document.getElementById('deleteInventoryBtn').onclick = function(e) {
    e.preventDefault();
    if(!confirm('정말 삭제하시겠습니까?')) return;
    const id = document.querySelector('#inventoryEditForm [name="id"]').value;
    fetch('/inventory/api/delete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id})
    }).then(res => res.json()).then(result => {
      if(result.success) {
        bootstrap.Modal.getInstance(document.getElementById('inventoryEditModal')).hide();
        loadInventoryTable();
        alert('삭제되었습니다.');
      } else {
        alert('삭제 실패: ' + (result.message || '오류'));
      }
    });
  };

// 최초 로딩 및 이벤트 바인딩
window.addEventListener('DOMContentLoaded',()=>{
  loadProjectTypes();
  loadRequests();
  loadInventoryTable();

  // 품목 추가 버튼 클릭 시(모달 오픈)
  document.getElementById('addInventoryBtn').onclick = function() {
    const modalEl = document.getElementById('inventoryModal');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) modal = new bootstrap.Modal(modalEl);
    modal.show();
  };

  // 품목 추가 폼 제출
  document.getElementById('submitInventoryBtn').onclick = function(e) {
    e.preventDefault();
    const form = document.getElementById('inventoryForm');
    const fd = new FormData(form);
    const data = Object.fromEntries(fd.entries());
    fetch('/inventory/api/add', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    }).then(res => res.json()).then(result => {
      if(result.success) {
        bootstrap.Modal.getInstance(document.getElementById('inventoryModal')).hide();
        form.reset();
        loadInventoryTable();
        alert('품목이 추가되었습니다.');
      } else {
        alert('추가 실패: ' + (result.message || '오류'));
      }
    });
  };

  // 신규 구매 요청 모달 열기
  document.getElementById('openRequestModalBtn').onclick = ()=>{
    const modalEl = document.getElementById('requestModal');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if(modalEl.classList.contains('show')) {
      modal.hide();
      setTimeout(()=>{
        modal = new bootstrap.Modal(modalEl);
        modal.show();
        // 모달이 완전히 열린 후 이벤트 바인딩
        setTimeout(bindTotalPriceEvents, 100);
      }, 300);
    } else {
      modal = new bootstrap.Modal(modalEl);
      modal.show();
      // 모달이 완전히 열린 후 이벤트 바인딩
      setTimeout(bindTotalPriceEvents, 100);
    }
  };

  // 폼 제출(모달 내부)
  document.getElementById('submitRequestBtn').onclick = function(e) {
    e.preventDefault();
    const form = document.getElementById('purchaseForm');
    const fd = new FormData(form);
    const data = Object.fromEntries(fd.entries());
    
    // 디버깅: 원본 데이터 출력
    console.log('원본 데이터:', data);
    
    // 모든 필드에 대해 안전한 값 처리
    Object.keys(data).forEach(key => {
      if (data[key] === '' || data[key] === null || data[key] === undefined) {
        data[key] = '';
      } else if (typeof data[key] === 'string' && data[key].trim() === '') {
        data[key] = '';
      }
    });
    
    // 숫자 필드 NaN 방지: 빈 값이면 0으로 변환
    ['purchase_qty','unit_price','required_qty','safety_stock','total_price'].forEach(k=>{
      if(data[k] === '' || data[k] == null || data[k] === undefined) {
        data[k] = 0;
      } else if(typeof data[k] === 'string') {
        // 콤마 제거 후 숫자 변환
        const numVal = Number(data[k].replace(/,/g, ''));
        data[k] = isNaN(numVal) ? 0 : numVal;
      } else {
        const numVal = Number(data[k]);
        data[k] = isNaN(numVal) ? 0 : numVal;
      }
    });
    
    // 디버깅: 처리된 데이터 출력
    console.log('처리된 데이터:', data);
    
    if(!data.item || !data.purchase_qty || !data.unit_price || !data.requester || !data.project_type) {
      showToast('필수 항목을 입력하세요.','warning'); return;
    }
    data.total_price = Number(data.purchase_qty) * Number(data.unit_price);
    
    // 최종 데이터 검증
    console.log('최종 전송 데이터:', data);
    
    // 수정 모드 여부 확인
    const editId = form.getAttribute('data-edit-id');
    if(editId) {
      // 수정 API 호출
      fetch(`/purchasing/requests/update/${editId}`,{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)
      }).then(r=>r.json()).then(res=>{
        if(res.success) {
          showToast('수정이 완료되었습니다.','success');
          form.reset();
          form.removeAttribute('data-edit-id');
          document.getElementById('filterItem').value = '';
          document.getElementById('filterRequester').value = '';
          document.getElementById('filterProjectType').value = '';
          updateTotalPrice();
          loadRequests(true);
          bootstrap.Modal.getInstance(document.getElementById('requestModal')).hide();
        } else showToast('수정 실패','danger');
      }).catch(error => {
        console.error('수정 전송 에러:', error);
        showToast('수정 중 오류가 발생했습니다.','danger');
      });
    } else {
      // 신규 등록
      fetch('/purchasing/requests/add',{
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)
      }).then(r=>r.json()).then(res=>{
        if(res.success) {
          showToast('구매 요청이 등록되었습니다.','success');
          form.reset();
          document.getElementById('filterItem').value = '';
          document.getElementById('filterRequester').value = '';
          document.getElementById('filterProjectType').value = '';
          updateTotalPrice();
          loadRequests(true);
          bootstrap.Modal.getInstance(document.getElementById('requestModal')).hide();
        } else showToast('등록 실패','danger');
      }).catch(error => {
        console.error('전송 에러:', error);
        showToast('전송 중 오류가 발생했습니다.','danger');
      });
    }
  };

  // 테이블 정렬 기능
  let sortKey = null, sortAsc = true;
  document.querySelectorAll('#requestTable th[data-sort]').forEach(th=>{
    th.style.cursor = 'pointer';
    th.onclick = function() {
      const key = th.getAttribute('data-sort');
      if(sortKey === key) sortAsc = !sortAsc;
      else { sortKey = key; sortAsc = true; }
      requests.sort((a,b)=>{
        if(a[key]===b[key]) return 0;
        if(a[key]==null) return 1;
        if(b[key]==null) return -1;
        if(!isNaN(a[key]) && !isNaN(b[key])) return (Number(a[key])-Number(b[key]))*(sortAsc?1:-1);
        return (a[key]+'').localeCompare(b[key]+'',undefined,{numeric:true})*(sortAsc?1:-1);
      });
      renderTable();
    };
  });

  document.getElementById('manageProjectTypeBtn').onclick = ()=>{
    loadProjectTypes();
    const modalEl = document.getElementById('projectTypeModal');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if(modalEl.classList.contains('show')) {
      // 이미 열려 있으면 닫고, 닫힌 후 다시 열기
      modal.hide();
      setTimeout(()=>{
        modal = new bootstrap.Modal(modalEl);
        modal.show();
      }, 300); // 닫힘 애니메이션 시간 후 show
    } else {
      modal = new bootstrap.Modal(modalEl);
      modal.show();
    }
  };
  document.getElementById('addProjectTypeBtn').onclick = ()=>{
    const val = document.getElementById('newProjectType').value.trim();
    if(!val) return showToast('국책과제명을 입력하세요.','warning');
    fetch('/purchasing/project-types/add',{
      method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_type:val})
    }).then(r=>r.json()).then(res=>{
      if(res.success) { showToast('추가되었습니다.','success'); document.getElementById('newProjectType').value=''; loadProjectTypes(); renderProjectTypeSelect(); }
      else showToast(res.error||'추가 실패','danger');
    });
  };
  ['filterItem','filterRequester','filterProjectType'].forEach(id=>{
    document.getElementById(id).addEventListener('input', loadRequests);
    document.getElementById(id).addEventListener('change', loadRequests);
  });
});

// 수정
window.editRequest = function(id) {
  const req = requests.find(r=>r.id===id);
  if(!req) return;
  const form = document.getElementById('purchaseForm');
  // 폼에 값 채우기
  Object.entries(req).forEach(([k,v])=>{
    if(form[k]) form[k].value = v;
  });
  // 수정 모드 표시
  form.setAttribute('data-edit-id', id);
  showToast('수정 후 저장하면 변경됩니다.','info');
  // 모달 열기
  const modalEl = document.getElementById('requestModal');
  let modal = bootstrap.Modal.getInstance(modalEl);
  if(!modalEl.classList.contains('show')) {
    modal = new bootstrap.Modal(modalEl);
    modal.show();
    setTimeout(bindTotalPriceEvents, 100);
  }
};
// 삭제
window.deleteRequest = function(id, silent) {
  if(!silent && !confirm('정말 삭제하시겠습니까?')) return;
  fetch(`/purchasing/requests/delete/${id}`,{method:'POST'}).then(r=>r.json()).then(res=>{
    if(res.success) { if(!silent) showToast('삭제되었습니다.','success'); loadRequests(); }
    else showToast('삭제 실패','danger');
  });
};

// 구매 상태 토글 함수
window.togglePurchaseStatus = function(id) {
  console.log('구매 상태 변경 시도:', id);
  
  fetch(`/purchasing/requests/toggle-status/${id}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => {
    console.log('응답 상태:', response.status);
    return response.json();
  }).then(res => {
    console.log('응답 데이터:', res);
    if (res.success) {
      showToast(`구매 상태가 '${res.new_status}'로 변경되었습니다.`, 'success');
      loadRequests(); // 테이블 새로고침
    } else {
      console.error('서버 에러:', res.error);
      showToast(`상태 변경 실패: ${res.error || '알 수 없는 오류'}`, 'danger');
    }
  }).catch(error => {
    console.error('네트워크 에러:', error);
    showToast('상태 변경 중 네트워크 오류가 발생했습니다.', 'danger');
  });
}; 