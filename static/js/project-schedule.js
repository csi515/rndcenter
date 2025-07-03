// 프로젝트 일정 관리 스크립트
// 요구: 3개월 연속, 이중 헤더, 셀 병합, 인라인 편집, 상세, 필터, 행 추가, CSV API 연동

let calendarMonths = [];
let scheduleData = [];
let filterProjectId = '';
let currentYear = dayjs().year();
let currentMonth = dayjs().month() + 1;
let projects = [];

// 날짜 계산: 지난달, 이번달, 다음달
function getCalendarMonths() {
  // 현재 월 기준으로 3개월(이전, 현재, 다음)
  const months = [];
  for (let i = -1; i <= 1; i++) {
    const m = dayjs(`${currentYear}-${currentMonth}-01`).add(i, 'month');
    months.push({ year: m.year(), month: m.month() + 1 });
  }
  return months;
}

function updateMonthLabel() {
  const label = document.getElementById('currentMonthLabel');
  label.textContent = `${currentYear}년 ${currentMonth}월`;
}

// 헤더 렌더링
function renderCalendarHeader() {
  calendarMonths = getCalendarMonths();
  let monthRow = '<tr>';
  let weekRow = '<tr>';
  monthRow += '<th rowspan="2" class="project-header">연구 프로젝트</th>';
  calendarMonths.forEach(m => {
    monthRow += `<th class="month-header" colspan="4">${m.month}월</th>`;
  });
  monthRow += '</tr>';
  calendarMonths.forEach(m => {
    for (let w = 1; w <= 4; w++) {
      weekRow += `<th class="week-header">${w}주차</th>`;
    }
  });
  weekRow += '</tr>';
  document.getElementById('calendarHeader').innerHTML = monthRow + weekRow;
}

// 바디 렌더링
function renderCalendarBody() {
  let rows = '';
  // 프로젝트별로 그룹핑
  const projectMap = {};
  (window.projects || []).forEach(p => {
    projectMap[p.id] = p.name;
  });
  const projectIds = Object.keys(projectMap);
  projectIds.forEach(pid => {
    rows += `<tr data-project-id="${pid}"><td class="project-name">${projectMap[pid]}</td>`;
    calendarMonths.forEach(m => {
      for (let w = 1; w <= 4; w++) {
        const cellData = scheduleData.find(d => d.project_id === pid && d.year == m.year && d.month == m.month && d.week == w);
        if (cellData) {
          const merged = cellData.merged_weeks ? parseInt(cellData.merged_weeks) : 1;
          if (!cellData._rendered) {
            rows += `<td class="editable merged" colspan="${merged}" data-id="${cellData.id}" data-project-id="${pid}" data-year="${m.year}" data-month="${m.month}" data-week="${w}">
              <span class="summary-text">${cellData.summary || ''}</span>
              <span class="expand-btn" onclick="toggleDetail(this)">▶</span>
              <div class="detail-content">${cellData.detail || ''}</div>
            </td>`;
            cellData._rendered = true;
            w += merged - 1;
          }
        } else {
          rows += `<td class="editable" data-project-id="${pid}" data-year="${m.year}" data-month="${m.month}" data-week="${w}"></td>`;
        }
      }
    });
    rows += '</tr>';
  });
  document.getElementById('calendarBody').innerHTML = rows;
}

// 상세 토글
window.toggleDetail = function(btn) {
  const detail = btn.parentElement.querySelector('.detail-content');
  detail.classList.toggle('open');
  btn.textContent = detail.classList.contains('open') ? '▼' : '▶';
};

// 셀 클릭(인라인 편집)
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('editable')) {
    editCell(e.target);
  }
});

function editCell(cell) {
  const oldSummary = cell.querySelector('.summary-text') ? cell.querySelector('.summary-text').textContent : '';
  const oldDetail = cell.querySelector('.detail-content') ? cell.querySelector('.detail-content').textContent : '';
  cell.innerHTML = `<input type="text" class="form-control form-control-sm mb-1" value="${oldSummary}" placeholder="요약(한줄)" autofocus>
    <textarea class="form-control form-control-sm" rows="2" placeholder="상세내용">${oldDetail}</textarea>
    <button class="btn btn-sm btn-success mt-1 save-btn">저장</button>
    <button class="btn btn-sm btn-secondary mt-1 cancel-btn">취소</button>`;
  cell.querySelector('input').focus();
  cell.querySelector('.save-btn').onclick = function() { saveCell(cell); };
  cell.querySelector('.cancel-btn').onclick = function() { renderCalendarBody(); };
}

function saveCell(cell) {
  const summary = cell.querySelector('input').value;
  const detail = cell.querySelector('textarea').value;
  const researcher_id = cell.getAttribute('data-researcher-id');
  const year = cell.getAttribute('data-year');
  const month = cell.getAttribute('data-month');
  const week = cell.getAttribute('data-week');
  const id = cell.getAttribute('data-id');
  const project_id = filterProjectId || cell.getAttribute('data-project-id') || '';
  const project = (window.projects || []).find(p => p.id == project_id);
  const project_name = project ? project.name : '';
  const data = {
    id,
    researcher_id,
    researcher_name: (window.researchers || []).find(r => r.id == researcher_id)?.name || '',
    year,
    month,
    week,
    summary,
    detail,
    merged_weeks: 1,
    project_id,
    project_name
  };
  fetch('/api/project-schedule/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()).then(res => {
    showFeedback('저장되었습니다.', 'success');
    loadScheduleData();
  });
}

// 필터
const projectFilter = document.getElementById('projectFilter');
if (projectFilter) {
  projectFilter.addEventListener('change', function() {
    filterProjectId = this.value;
    loadScheduleData();
  });
}

const prevMonthBtn = document.getElementById('prevMonthBtn');
const nextMonthBtn = document.getElementById('nextMonthBtn');
prevMonthBtn.addEventListener('click', function() {
  currentMonth--;
  if (currentMonth < 1) {
    currentMonth = 12;
    currentYear--;
  }
  updateMonthLabel();
  renderCalendarHeader();
  loadScheduleData();
});
nextMonthBtn.addEventListener('click', function() {
  currentMonth++;
  if (currentMonth > 12) {
    currentMonth = 1;
    currentYear++;
  }
  updateMonthLabel();
  renderCalendarHeader();
  loadScheduleData();
});

// 행 추가
const addRowBtn = document.getElementById('addRowBtn');
addRowBtn.addEventListener('click', function() {
  // 연구원 추가 모달 등 구현 필요. 여기선 샘플로 첫 연구원 추가
  alert('연구원 추가 기능은 추후 구현 예정입니다.');
});

// 데이터 불러오기
function loadScheduleData() {
  fetch(`/api/project-schedule?year=${currentYear}&month=${currentMonth}${filterProjectId ? `&project_id=${filterProjectId}` : ''}`)
    .then(r => r.json())
    .then(data => {
      scheduleData = data;
      // 렌더링 전 _rendered 플래그 초기화
      scheduleData.forEach(d => { delete d._rendered; });
      renderCalendarBody();
    });
}

// 피드백 메시지
function showFeedback(msg, type) {
  const el = document.getElementById('feedbackMsg');
  el.innerHTML = `<div class="alert alert-${type == 'success' ? 'success' : 'info'}">${msg}</div>`;
  setTimeout(() => { el.innerHTML = ''; }, 2000);
}

// 프로젝트 목록 및 일정 데이터 불러오기
function loadProjectsAndRenderTable() {
  fetch('/research/projects/api')
    .then(res => res.json())
    .then(data => {
      projects = data;
      renderScheduleTable();
      fillProjectSelect();
    });
}

// 프로젝트 셀렉트박스 채우기
function fillProjectSelect() {
  const select = document.getElementById('scheduleProject');
  if (!select) return;
  select.innerHTML = '';
  projects.forEach(p => {
    const option = document.createElement('option');
    option.value = p.name;
    option.textContent = p.name;
    select.appendChild(option);
  });
}

// 일정 데이터 불러오기 (월/주차별)
function loadScheduleDataAndRender() {
  fetch('/research/api/schedule')
    .then(res => res.json())
    .then(data => {
      scheduleData = data;
      renderScheduleTable();
    });
}

// 표 렌더링
function renderScheduleTable() {
  const tbody = document.querySelector('#scheduleTable tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  projects.forEach(project => {
    let tr = document.createElement('tr');
    let tdName = document.createElement('td');
    tdName.textContent = project.name;
    tr.appendChild(tdName);
    for (let m = 6; m <= 8; m++) {
      for (let w = 1; w <= 4; w++) {
        let td = document.createElement('td');
        td.classList.add('schedule-cell');
        td.dataset.project = project.name;
        td.dataset.month = m;
        td.dataset.week = w;
        // 일정 데이터 표시
        let found = (scheduleData.events || []).find(ev => ev.project === project.name && Number(ev.start_date?.split('-')[1]) === m && Number(ev.week) === w);
        td.textContent = found ? found.task : '';
        td.onclick = function() {
          openAddScheduleModal(project.name, m, w, found ? found.task : '');
        };
        tr.appendChild(td);
      }
    }
    tbody.appendChild(tr);
  });
}

// 셀 클릭 시 모달 오픈 및 값 세팅
function openAddScheduleModal(project, month, week, task) {
  document.getElementById('scheduleProject').value = project;
  document.getElementById('scheduleMonth').value = month;
  document.getElementById('scheduleWeek').value = week;
  document.getElementById('scheduleTask').value = task || '';
  new bootstrap.Modal(document.getElementById('addScheduleModal')).show();
}

// 폼 제출 시 일정 추가
const addScheduleForm = document.getElementById('addScheduleForm');
if (addScheduleForm) {
  addScheduleForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(addScheduleForm);
    fetch('/research/schedule/add', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        loadScheduleDataAndRender();
        bootstrap.Modal.getInstance(document.getElementById('addScheduleModal')).hide();
        addScheduleForm.reset();
      } else {
        alert('일정 추가 중 오류가 발생했습니다.');
      }
    });
  });
}

// 초기화
updateMonthLabel();
renderCalendarHeader();
loadScheduleData();
window.addEventListener('DOMContentLoaded', function() {
  loadProjectsAndRenderTable();
  loadScheduleDataAndRender();
}); 