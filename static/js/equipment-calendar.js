let calendar;
let equipmentColors = {};

function initializeEquipmentCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        height: 'auto',
        locale: 'ko',
        firstDay: 0, // Sunday first
        dayHeaderFormat: { weekday: 'short' },
        dayCellContent: function(arg) {
            return arg.dayNumberText.replace('일', '');
        },
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
            startTime: '09:00',
            endTime: '18:00'
        },
        selectable: true,
        selectMirror: true,
        editable: true,
        dayMaxEvents: true,
        weekNumbers: false,
        navLinks: true,
        
        // Event sources
        events: '/equipment/api/reservations',
        
        // Selection callback - for creating new events
        select: function(selectionInfo) {
            const startDate = selectionInfo.startStr.split('T')[0];
            const endDate = selectionInfo.endStr.split('T')[0];
            
            // Adjust end date for all-day selections
            let adjustedEndDate = startDate;
            if (selectionInfo.allDay && endDate !== startDate) {
                const endDateObj = new Date(endDate);
                endDateObj.setDate(endDateObj.getDate() - 1);
                adjustedEndDate = endDateObj.toISOString().split('T')[0];
            }
            
            showAddReservationModal(startDate, adjustedEndDate);
            calendar.unselect();
        },
        
        // Event click callback - for editing events
        eventClick: function(clickInfo) {
            showEventDetails(clickInfo.event);
        },
        
        // Event drag & drop callback
        eventDrop: function(dropInfo) {
            updateEventTiming(dropInfo.event);
        },
        
        // Event resize callback
        eventResize: function(resizeInfo) {
            updateEventTiming(resizeInfo.event);
        },
        
        // Event render callback
        eventDidMount: function(mountInfo) {
            // Add tooltip
            const event = mountInfo.event;
            const el = mountInfo.el;
            
            const tooltip = `
                <strong>${event.extendedProps.equipment_name}</strong><br>
                예약자: ${event.extendedProps.reserver}<br>
                목적: ${event.extendedProps.purpose || '없음'}<br>
                상태: ${event.extendedProps.status}
            `;
            
            el.setAttribute('title', tooltip);
            el.setAttribute('data-bs-toggle', 'tooltip');
            el.setAttribute('data-bs-html', 'true');
            
            // Initialize Bootstrap tooltip
            new bootstrap.Tooltip(el);
        },
        
        // Loading callback
        loading: function(isLoading) {
            if (isLoading) {
                showProgress();
            } else {
                hideProgress();
                updateEquipmentLegend();
            }
        },
        
        // Error handling
        eventSourceFailure: function(errorObj) {
            console.error('Failed to load events:', errorObj);
            showNotification('예약 데이터를 불러오는데 실패했습니다.', 'error');
        }
    });
    
    calendar.render();
    
    // Setup view buttons
    setupViewControls();
}

function setupViewControls() {
    // Add custom controls if needed
    const toolbar = document.querySelector('.fc-toolbar-chunk');
    if (toolbar) {
        // Custom view controls can be added here
    }
}

function updateEventTiming(event) {
    const payload = {
        start: event.start.toISOString(),
        end: event.end ? event.end.toISOString() : event.start.toISOString()
    };
    
    fetch(`/equipment/reservations/update/${event.id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('예약 시간이 변경되었습니다.', 'success');
        } else {
            showNotification(result.message, 'error');
            calendar.refetchEvents(); // Revert changes
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('시간 변경 중 오류가 발생했습니다.', 'error');
        calendar.refetchEvents(); // Revert changes
    });
}

function showEventDetails(event) {
    const startDate = new Date(event.start);
    const endDate = event.end ? new Date(event.end) : startDate;
    
    const formatDate = (date) => {
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'short'
        });
    };
    
    const formatTime = (date) => {
        return date.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };
    
    const isAllDay = event.allDay || 
        (startDate.getHours() === 0 && startDate.getMinutes() === 0 && 
         endDate.getHours() === 23 && endDate.getMinutes() === 59);
    
    let timeDisplay;
    if (isAllDay) {
        if (startDate.toDateString() === endDate.toDateString()) {
            timeDisplay = `${formatDate(startDate)} (하루 종일)`;
        } else {
            timeDisplay = `${formatDate(startDate)} ~ ${formatDate(endDate)} (하루 종일)`;
        }
    } else {
        if (startDate.toDateString() === endDate.toDateString()) {
            timeDisplay = `${formatDate(startDate)} ${formatTime(startDate)} ~ ${formatTime(endDate)}`;
        } else {
            timeDisplay = `${formatDate(startDate)} ${formatTime(startDate)} ~ ${formatDate(endDate)} ${formatTime(endDate)}`;
        }
    }
    
    const content = `
        <div class="event-details">
            <p><strong>장비:</strong> ${event.extendedProps.equipment_name}</p>
            <p><strong>예약자:</strong> ${event.extendedProps.reserver}</p>
            <p><strong>일시:</strong> ${timeDisplay}</p>
            <p><strong>목적:</strong> ${event.extendedProps.purpose || '없음'}</p>
            <p><strong>상태:</strong> <span class="badge bg-primary">${event.extendedProps.status}</span></p>
            ${event.extendedProps.notes ? `<p><strong>메모:</strong> ${event.extendedProps.notes}</p>` : ''}
        </div>
    `;
    
    document.getElementById('eventDetailsContent').innerHTML = content;
    
    // Store current event for edit button
    window.currentEventForEdit = event;
    
    new bootstrap.Modal(document.getElementById('eventDetailsModal')).show();
}

function editEventFromDetails() {
    if (window.currentEventForEdit) {
        bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal')).hide();
        editReservation(window.currentEventForEdit);
    }
}

function updateEquipmentLegend() {
    const legendContainer = document.getElementById('equipmentLegend');
    if (!legendContainer) return;
    
    // Get unique equipment names from current events
    const events = calendar.getEvents();
    const equipmentNames = [...new Set(events.map(event => event.extendedProps.equipment_name))];
    
    legendContainer.innerHTML = '';
    
    equipmentNames.forEach(equipment => {
        const color = getEquipmentColorFromHash(equipment);
        const legendItem = document.createElement('div');
        legendItem.className = 'equipment-legend-item';
        legendItem.innerHTML = `
            <div class="equipment-color" style="background-color: ${color};"></div>
            <span>${equipment}</span>
        `;
        legendContainer.appendChild(legendItem);
    });
    
    if (equipmentNames.length === 0) {
        legendContainer.innerHTML = '<em class="text-muted">예약된 장비가 없습니다.</em>';
    }
}

function getEquipmentColorFromHash(equipmentName) {
    // Use the same color algorithm as the backend
    const colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14'];
    
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < equipmentName.length; i++) {
        const char = equipmentName.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    
    return colors[Math.abs(hash) % colors.length];
}

// Calendar view controls
function switchView(viewName) {
    calendar.changeView(viewName);
}

function goToToday() {
    calendar.today();
}

function goToPrevious() {
    calendar.prev();
}

function goToNext() {
    calendar.next();
}

function refreshCalendar() {
    calendar.refetchEvents();
}

// Filter functions
function filterByEquipment(equipmentName) {
    // Filter events by equipment
    const events = calendar.getEvents();
    events.forEach(event => {
        if (equipmentName === '' || event.extendedProps.equipment_name === equipmentName) {
            event.setProp('display', 'auto');
        } else {
            event.setProp('display', 'none');
        }
    });
}

function filterByStatus(status) {
    // Filter events by status
    const events = calendar.getEvents();
    events.forEach(event => {
        if (status === '' || event.extendedProps.status === status) {
            event.setProp('display', 'auto');
        } else {
            event.setProp('display', 'none');
        }
    });
}

// Utility functions
function showProgress() {
    // Show loading indicator
    const progressHtml = `
        <div id="loadingIndicator" class="d-flex justify-content-center align-items-center position-fixed" 
             style="top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.8); z-index: 9999;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">로딩 중...</span>
            </div>
        </div>
    `;
    
    if (!document.getElementById('loadingIndicator')) {
        document.body.insertAdjacentHTML('beforeend', progressHtml);
    }
}

function hideProgress() {
    const indicator = document.getElementById('loadingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Export calendar data to CSV
function exportReservationsToCSV() {
    const events = calendar.getEvents();
    const csvData = [
        ['장비명', '예약자', '시작일시', '종료일시', '목적', '상태', '메모']
    ];
    
    events.forEach(event => {
        csvData.push([
            event.extendedProps.equipment_name,
            event.extendedProps.reserver,
            event.start.toISOString(),
            event.end ? event.end.toISOString() : event.start.toISOString(),
            event.extendedProps.purpose || '',
            event.extendedProps.status,
            event.extendedProps.notes || ''
        ]);
    });
    
    const csvContent = csvData.map(row => row.map(field => `"${field}"`).join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `equipment_reservations_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Print calendar
function printCalendar() {
    window.print();
}