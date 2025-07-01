// Schedule management with FullCalendar integration

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeScheduleForm();
});

let calendar;

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        locale: 'ko',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: '오늘',
            month: '월',
            week: '주',
            day: '일'
        },
        height: 'auto',
        slotMinTime: '07:00:00',
        slotMaxTime: '22:00:00',
        weekends: true,
        editable: true,
        droppable: true,
        selectable: true,
        selectMirror: true,
        dayMaxEvents: true,
        
        // Event sources
        events: {
            url: '/research/api/schedule',
            method: 'GET',
            failure: function() {
                showNotification('일정을 불러오는 중 오류가 발생했습니다.', 'danger');
            }
        },

        // Event rendering
        eventDidMount: function(info) {
            // Add tooltips to events
            info.el.setAttribute('data-bs-toggle', 'tooltip');
            info.el.setAttribute('data-bs-placement', 'top');
            info.el.setAttribute('title', 
                `프로젝트: ${info.event.extendedProps.project || '미지정'}\n` +
                `상태: ${info.event.extendedProps.status || '예정'}\n` +
                `메모: ${info.event.extendedProps.notes || '없음'}`
            );
            
            // Initialize tooltip
            new bootstrap.Tooltip(info.el);
        },

        // Event interactions
        eventClick: function(info) {
            showEventDetails(info.event);
        },

        select: function(info) {
            showAddEventDialog(info);
        },

        eventDrop: function(info) {
            updateEventTiming(info.event);
        },

        eventResize: function(info) {
            updateEventTiming(info.event);
        },

        // Resource configuration for researcher view
        resourceAreaHeaderContent: '연구원',
        resources: function(fetchInfo, successCallback, failureCallback) {
            // Fetch researchers for resource view
            fetch('/research/api/researchers')
                .then(response => response.json())
                .then(data => {
                    const resources = data.map(researcher => ({
                        id: researcher.name,
                        title: researcher.name
                    }));
                    successCallback(resources);
                })
                .catch(error => {
                    console.error('Failed to load researchers:', error);
                    failureCallback(error);
                });
        }
    });

    calendar.render();
}

function initializeScheduleForm() {
    const scheduleForm = document.getElementById('addScheduleForm');
    if (!scheduleForm) return;

    scheduleForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(scheduleForm);
        
        fetch('/research/schedule/add', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                calendar.refetchEvents();
                bootstrap.Modal.getInstance(document.getElementById('addScheduleModal')).hide();
                scheduleForm.reset();
            } else {
                showNotification(data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error adding schedule:', error);
            showNotification('일정 추가 중 오류가 발생했습니다.', 'danger');
        });
    });
}

function showEventDetails(event) {
    const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal') || createEventDetailsModal());
    
    const modalBody = document.querySelector('#eventDetailsModal .modal-body');
    modalBody.innerHTML = `
        <div class="row mb-3">
            <div class="col-4"><strong>제목:</strong></div>
            <div class="col-8">${event.title}</div>
        </div>
        <div class="row mb-3">
            <div class="col-4"><strong>연구원:</strong></div>
            <div class="col-8">${event.getResources().map(r => r.title).join(', ') || '미지정'}</div>
        </div>
        <div class="row mb-3">
            <div class="col-4"><strong>프로젝트:</strong></div>
            <div class="col-8">${event.extendedProps.project || '미지정'}</div>
        </div>
        <div class="row mb-3">
            <div class="col-4"><strong>시작일시:</strong></div>
            <div class="col-8">${formatDateTime(event.start)}</div>
        </div>
        <div class="row mb-3">
            <div class="col-4"><strong>종료일시:</strong></div>
            <div class="col-8">${formatDateTime(event.end)}</div>
        </div>
        <div class="row mb-3">
            <div class="col-4"><strong>상태:</strong></div>
            <div class="col-8">
                <span class="badge ${getStatusBadgeClass(event.extendedProps.status)}">
                    ${event.extendedProps.status || '예정'}
                </span>
            </div>
        </div>
        ${event.extendedProps.notes ? `
        <div class="row mb-3">
            <div class="col-4"><strong>메모:</strong></div>
            <div class="col-8">${event.extendedProps.notes}</div>
        </div>
        ` : ''}
    `;
    
    modal.show();
}

function createEventDetailsModal() {
    const modalHtml = `
        <div class="modal fade" id="eventDetailsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">일정 상세</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- Content will be filled dynamically -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                        <button type="button" class="btn btn-primary" onclick="editEvent()">수정</button>
                        <button type="button" class="btn btn-danger" onclick="deleteEvent()">삭제</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    return document.getElementById('eventDetailsModal');
}

function showAddEventDialog(selectionInfo) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('addScheduleModal'));
    
    // Pre-fill dates based on selection
    const startDate = selectionInfo.start.toISOString().split('T')[0];
    const endDate = selectionInfo.end.toISOString().split('T')[0];
    const startTime = selectionInfo.start.toTimeString().split(' ')[0].substring(0, 5);
    const endTime = selectionInfo.end.toTimeString().split(' ')[0].substring(0, 5);
    
    document.querySelector('[name="start_date"]').value = startDate;
    document.querySelector('[name="end_date"]').value = endDate;
    document.querySelector('[name="start_time"]').value = startTime;
    document.querySelector('[name="end_time"]').value = endTime;
    
    modal.show();
}

function updateEventTiming(event) {
    const eventData = {
        id: event.id,
        start: event.start.toISOString(),
        end: event.end ? event.end.toISOString() : null
    };
    
    fetch('/research/schedule/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('일정이 업데이트되었습니다.', 'success');
        } else {
            showNotification('일정 업데이트에 실패했습니다.', 'danger');
            calendar.refetchEvents(); // Revert changes
        }
    })
    .catch(error => {
        console.error('Error updating event:', error);
        showNotification('일정 업데이트 중 오류가 발생했습니다.', 'danger');
        calendar.refetchEvents(); // Revert changes
    });
}

function switchView(viewName) {
    if (calendar) {
        calendar.changeView(viewName);
    }
}

function goToToday() {
    if (calendar) {
        calendar.today();
    }
}

function goToPrevious() {
    if (calendar) {
        calendar.prev();
    }
}

function goToNext() {
    if (calendar) {
        calendar.next();
    }
}

function refreshSchedule() {
    if (calendar) {
        calendar.refetchEvents();
        showNotification('일정이 새로고침되었습니다.', 'info');
    }
}

function filterByResearcher(researcherName) {
    if (calendar) {
        calendar.getEvents().forEach(event => {
            if (researcherName === '' || event.getResources().some(r => r.title === researcherName)) {
                event.setProp('display', 'auto');
            } else {
                event.setProp('display', 'none');
            }
        });
    }
}

function filterByProject(projectName) {
    if (calendar) {
        calendar.getEvents().forEach(event => {
            if (projectName === '' || event.extendedProps.project === projectName) {
                event.setProp('display', 'auto');
            } else {
                event.setProp('display', 'none');
            }
        });
    }
}

function filterByStatus(status) {
    if (calendar) {
        calendar.getEvents().forEach(event => {
            if (status === '' || event.extendedProps.status === status) {
                event.setProp('display', 'auto');
            } else {
                event.setProp('display', 'none');
            }
        });
    }
}

function exportScheduleToCSV() {
    const events = calendar.getEvents();
    const csvData = [];
    
    // CSV headers
    csvData.push(['연구원', '프로젝트', '작업', '시작일시', '종료일시', '상태', '메모']);
    
    // Add event data
    events.forEach(event => {
        csvData.push([
            event.getResources().map(r => r.title).join(', '),
            event.extendedProps.project || '',
            event.title,
            formatDateTime(event.start),
            formatDateTime(event.end),
            event.extendedProps.status || '예정',
            event.extendedProps.notes || ''
        ]);
    });
    
    // Create CSV content
    const csvContent = csvData.map(row => 
        row.map(cell => `"${cell}"`).join(',')
    ).join('\n');
    
    // Download CSV
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `schedule_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    showNotification('일정이 CSV 파일로 내보내졌습니다.', 'success');
}

// Utility functions
function formatDateTime(date) {
    if (!date) return '';
    return new Date(date).toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case '완료': return 'bg-success';
        case '진행중': return 'bg-primary';
        case '연기': return 'bg-warning';
        case '취소': return 'bg-danger';
        default: return 'bg-info';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 't':
                e.preventDefault();
                goToToday();
                break;
            case 'r':
                e.preventDefault();
                refreshSchedule();
                break;
            case 'n':
                e.preventDefault();
                document.querySelector('[data-bs-target="#addScheduleModal"]').click();
                break;
        }
    }
    
    // Navigation shortcuts
    switch (e.key) {
        case 'ArrowLeft':
            if (e.altKey) {
                e.preventDefault();
                goToPrevious();
            }
            break;
        case 'ArrowRight':
            if (e.altKey) {
                e.preventDefault();
                goToNext();
            }
            break;
    }
});

// Expose functions to global scope
window.ScheduleManager = {
    switchView,
    goToToday,
    goToPrevious,
    goToNext,
    refreshSchedule,
    filterByResearcher,
    filterByProject,
    filterByStatus,
    exportScheduleToCSV
};
