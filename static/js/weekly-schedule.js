// Weekly Schedule Management
class WeeklyScheduleManager {
    constructor() {
        this.currentDate = new Date();
        this.schedules = {};
        this.draggedElement = null;
        this.draggedFromWeek = null;
        
        this.init();
    }

    async init() {
        this.updateMonthDisplay();
        this.updateWeekDates();
        this.schedules = await this.loadSchedules();
        this.renderSchedules();
        this.bindEvents();
        this.initSortable();
    }

    // Date Management
    updateMonthDisplay() {
        const monthNames = [
            '1월', '2월', '3월', '4월', '5월', '6월',
            '7월', '8월', '9월', '10월', '11월', '12월'
        ];
        
        const year = this.currentDate.getFullYear();
        const month = monthNames[this.currentDate.getMonth()];
        
        document.getElementById('currentMonth').textContent = `${year}년 ${month}`;
    }

    updateWeekDates() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // Get first day of month
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // Calculate weeks
        const weeks = this.calculateWeeksInMonth(firstDay, lastDay);
        
        // Update week date displays
        weeks.forEach((week, index) => {
            const weekCard = document.querySelector(`[data-week="${index + 1}"]`);
            if (weekCard) {
                const datesElement = weekCard.parentElement.querySelector('.week-dates');
                if (week.start && week.end) {
                    datesElement.textContent = `${week.start.getDate()}일 - ${week.end.getDate()}일`;
                } else {
                    datesElement.textContent = '';
                }
            }
        });
    }

    calculateWeeksInMonth(firstDay, lastDay) {
        const weeks = [];
        const month = firstDay.getMonth();
        
        // Find the first Monday of the month or the first day if it's not Monday
        let currentDate = new Date(firstDay);
        
        for (let week = 0; week < 5; week++) {
            const weekStart = new Date(currentDate);
            const weekEnd = new Date(currentDate);
            weekEnd.setDate(weekEnd.getDate() + 6);
            
            // Check if this week has any days in the current month
            const hasMonthDays = (weekStart.getMonth() === month && weekStart.getDate() <= lastDay.getDate()) ||
                                (weekEnd.getMonth() === month && weekEnd.getDate() >= 1) ||
                                (weekStart.getMonth() < month && weekEnd.getMonth() >= month);
            
            if (hasMonthDays) {
                // Calculate actual start and end dates within the month
                const actualStart = weekStart.getMonth() === month ? weekStart : new Date(firstDay);
                const actualEnd = weekEnd.getMonth() === month ? weekEnd : new Date(lastDay);
                
                weeks.push({
                    start: actualStart,
                    end: actualEnd
                });
            } else {
                weeks.push({ start: null, end: null });
            }
            
            currentDate.setDate(currentDate.getDate() + 7);
        }
        
        return weeks;
    }

    // Schedule Management
    async loadSchedules() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth() + 1;
        
        try {
            const response = await fetch(`/research/api/weekly-schedule/${year}/${month}`);
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                console.error('Failed to load schedules from server');
                // Fallback to localStorage for backward compatibility
                const key = `schedules_${year}_${month}`;
                const saved = localStorage.getItem(key);
                
                if (saved) {
                    return JSON.parse(saved);
                } else if (year === 2025 && month === 1) {
                    return this.getSampleSchedules();
                }
                return {};
            }
        } catch (error) {
            console.error('Error loading schedules:', error);
            // Fallback to localStorage
            const key = `schedules_${year}_${month}`;
            const saved = localStorage.getItem(key);
            return saved ? JSON.parse(saved) : {};
        }
    }
    
    getSampleSchedules() {
        return {
            "1": [
                {
                    id: "sample_1",
                    task: "나노소재 합성 실험",
                    researcher: "김연구",
                    project: "나노복합소재 개발",
                    priority: "높음",
                    notes: "금 나노입자 합성 및 특성 분석",
                    createdAt: "2025-01-01T09:00:00.000Z"
                },
                {
                    id: "sample_2", 
                    task: "TEM 분석",
                    researcher: "박실험",
                    project: "나노복합소재 개발",
                    priority: "보통",
                    notes: "합성된 샘플의 미세구조 관찰",
                    createdAt: "2025-01-01T10:00:00.000Z"
                }
            ],
            "2": [
                {
                    id: "sample_3",
                    task: "태양전지 효율 측정",
                    researcher: "정에너지",
                    project: "고효율 태양전지 개발",
                    priority: "긴급",
                    notes: "새로운 전지 구조의 효율 평가",
                    createdAt: "2025-01-02T09:00:00.000Z"
                }
            ],
            "3": [
                {
                    id: "sample_4",
                    task: "단백질 정제",
                    researcher: "홍바이오",
                    project: "바이오센서 연구",
                    priority: "보통",
                    notes: "His-tag를 이용한 단백질 정제",
                    createdAt: "2025-01-03T09:00:00.000Z"
                },
                {
                    id: "sample_5",
                    task: "센서 성능 테스트",
                    researcher: "홍바이오",
                    project: "바이오센서 연구", 
                    priority: "높음",
                    notes: "정제된 단백질을 이용한 센서 테스트",
                    createdAt: "2025-01-03T10:00:00.000Z"
                }
            ]
        };
    }

    saveSchedules() {
        // Keep localStorage as backup
        const key = `schedules_${this.currentDate.getFullYear()}_${this.currentDate.getMonth() + 1}`;
        localStorage.setItem(key, JSON.stringify(this.schedules));
    }

    generateId() {
        return 'schedule_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async addSchedule(week, scheduleData) {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth() + 1;
        
        const requestData = {
            week: parseInt(week),
            month: month,
            year: year,
            task: scheduleData.task,
            researcher: scheduleData.researcher || '',
            project: scheduleData.project || '',
            priority: scheduleData.priority || '보통',
            notes: scheduleData.notes || ''
        };
        
        try {
            const response = await fetch('/research/schedule/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    // Reload schedules to update UI
                    this.schedules = await this.loadSchedules();
                    this.renderSchedules();
                    return result.schedule.id;
                }
            }
            throw new Error('Failed to add schedule');
        } catch (error) {
            console.error('Error adding schedule:', error);
            // Fallback to local storage
            const id = this.generateId();
            
            if (!this.schedules[week]) {
                this.schedules[week] = [];
            }
            
            this.schedules[week].push({
                id: id,
                task: scheduleData.task,
                researcher: scheduleData.researcher || '',
                project: scheduleData.project || '',
                priority: scheduleData.priority || '보통',
                notes: scheduleData.notes || '',
                createdAt: new Date().toISOString()
            });
            
            this.saveSchedules();
            this.renderSchedules();
            return id;
        }
    }

    async updateSchedule(id, week, scheduleData) {
        try {
            const response = await fetch(`/research/api/weekly-schedule/update/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(scheduleData)
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    // Reload schedules to update UI
                    this.schedules = await this.loadSchedules();
                    this.renderSchedules();
                    return;
                }
            }
            throw new Error('Failed to update schedule');
        } catch (error) {
            console.error('Error updating schedule:', error);
            // Fallback to local update
            for (let weekNum in this.schedules) {
                const scheduleIndex = this.schedules[weekNum].findIndex(s => s.id === id);
                if (scheduleIndex !== -1) {
                    this.schedules[weekNum][scheduleIndex] = {
                        ...this.schedules[weekNum][scheduleIndex],
                        ...scheduleData,
                        updatedAt: new Date().toISOString()
                    };
                    break;
                }
            }
            this.saveSchedules();
            this.renderSchedules();
        }
    }

    async deleteSchedule(id) {
        try {
            const response = await fetch(`/research/api/weekly-schedule/delete/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    // Reload schedules to update UI
                    this.schedules = await this.loadSchedules();
                    this.renderSchedules();
                    return;
                }
            }
            throw new Error('Failed to delete schedule');
        } catch (error) {
            console.error('Error deleting schedule:', error);
            // Fallback to local deletion
            for (let week in this.schedules) {
                this.schedules[week] = this.schedules[week].filter(s => s.id !== id);
            }
            this.saveSchedules();
            this.renderSchedules();
        }
    }

    async moveSchedule(id, fromWeek, toWeek) {
        if (fromWeek === toWeek) return;
        
        try {
            const response = await fetch(`/research/api/weekly-schedule/move/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ week: parseInt(toWeek) })
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    // Reload schedules to update UI
                    this.schedules = await this.loadSchedules();
                    this.renderSchedules();
                    return;
                }
            }
            throw new Error('Failed to move schedule');
        } catch (error) {
            console.error('Error moving schedule:', error);
            // Fallback to local move
            const scheduleIndex = this.schedules[fromWeek].findIndex(s => s.id === id);
            if (scheduleIndex === -1) return;
            
            const schedule = this.schedules[fromWeek][scheduleIndex];
            
            // Remove from old week
            this.schedules[fromWeek].splice(scheduleIndex, 1);
            
            // Add to new week
            if (!this.schedules[toWeek]) {
                this.schedules[toWeek] = [];
            }
            this.schedules[toWeek].push(schedule);
            
            this.saveSchedules();
            this.renderSchedules();
        }
    }

    // Rendering
    renderSchedules() {
        // Clear all week containers
        for (let week = 1; week <= 5; week++) {
            const container = document.getElementById(`week-${week}`);
            if (container) {
                container.innerHTML = '';
            }
        }
        
        // Render schedules for each week
        for (let week in this.schedules) {
            const container = document.getElementById(`week-${week}`);
            if (container) {
                this.schedules[week].forEach(schedule => {
                    const element = this.createScheduleElement(schedule, week);
                    container.appendChild(element);
                });
            }
        }
    }

    createScheduleElement(schedule, week) {
        const div = document.createElement('div');
        div.className = `schedule-item mb-2 p-2 border rounded ${this.getPriorityClass(schedule.priority)}`;
        div.draggable = true;
        div.dataset.scheduleId = schedule.id;
        div.dataset.week = week;
        
        div.innerHTML = `
            <div class="schedule-content">
                <div class="fw-bold">${this.escapeHtml(schedule.task)}</div>
                ${schedule.researcher ? `<small class="text-muted"><i class="fas fa-user"></i> ${this.escapeHtml(schedule.researcher)}</small><br>` : ''}
                ${schedule.project ? `<small class="text-muted"><i class="fas fa-project-diagram"></i> ${this.escapeHtml(schedule.project)}</small><br>` : ''}
                ${schedule.priority !== '보통' ? `<small class="badge bg-${this.getPriorityBadgeClass(schedule.priority)}">${schedule.priority}</small>` : ''}
            </div>
            <div class="schedule-actions">
                <button class="btn btn-sm btn-outline-secondary edit-schedule-btn" data-id="${schedule.id}">
                    <i class="fas fa-edit"></i>
                </button>
            </div>
        `;
        
        return div;
    }

    getPriorityClass(priority) {
        switch (priority) {
            case '긴급': return 'border-danger';
            case '높음': return 'border-warning';
            case '낮음': return 'border-secondary';
            default: return 'border-primary';
        }
    }

    getPriorityBadgeClass(priority) {
        switch (priority) {
            case '긴급': return 'danger';
            case '높음': return 'warning';
            case '낮음': return 'secondary';
            default: return 'primary';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Event Binding
    bindEvents() {
        // Month navigation
        document.getElementById('prevMonth').addEventListener('click', async () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.updateMonthDisplay();
            this.updateWeekDates();
            this.schedules = await this.loadSchedules();
            this.renderSchedules();
        });

        document.getElementById('nextMonth').addEventListener('click', async () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.updateMonthDisplay();
            this.updateWeekDates();
            this.schedules = await this.loadSchedules();
            this.renderSchedules();
        });

        // Add schedule buttons
        document.querySelectorAll('.add-schedule-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const week = e.target.dataset.week;
                this.showAddScheduleModal(week);
            });
        });

        // Modal forms
        document.getElementById('addScheduleForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddSchedule(e);
        });

        document.getElementById('editScheduleForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEditSchedule(e);
        });

        document.getElementById('deleteScheduleBtn').addEventListener('click', () => {
            this.handleDeleteSchedule();
        });

        // Edit schedule buttons (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.closest('.edit-schedule-btn')) {
                const btn = e.target.closest('.edit-schedule-btn');
                const id = btn.dataset.id;
                this.showEditScheduleModal(id);
            }
        });
    }

    // Drag and Drop
    initSortable() {
        document.querySelectorAll('.sortable-list').forEach(list => {
            list.addEventListener('dragover', this.handleDragOver.bind(this));
            list.addEventListener('drop', this.handleDrop.bind(this));
            list.addEventListener('dragenter', this.handleDragEnter.bind(this));
            list.addEventListener('dragleave', this.handleDragLeave.bind(this));
        });

        // Bind drag events to existing items
        document.addEventListener('dragstart', (e) => {
            if (e.target.classList.contains('schedule-item')) {
                this.draggedElement = e.target;
                this.draggedFromWeek = e.target.dataset.week;
                e.target.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', e.target.outerHTML);
            }
        });

        document.addEventListener('dragend', (e) => {
            if (e.target.classList.contains('schedule-item')) {
                e.target.classList.remove('dragging');
                this.draggedElement = null;
                this.draggedFromWeek = null;
                
                // Remove drag-over effects from all lists
                document.querySelectorAll('.sortable-list').forEach(list => {
                    list.classList.remove('drag-over');
                });
            }
        });
    }

    handleDragEnter(e) {
        e.preventDefault();
        e.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        // Only remove if we're actually leaving the element
        if (!e.currentTarget.contains(e.relatedTarget)) {
            e.currentTarget.classList.remove('drag-over');
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        
        if (!this.draggedElement) return;
        
        const targetWeek = e.currentTarget.id.split('-')[1];
        const scheduleId = this.draggedElement.dataset.scheduleId;
        
        if (this.draggedFromWeek !== targetWeek) {
            this.moveSchedule(scheduleId, this.draggedFromWeek, targetWeek);
            this.showNotification(`일정이 ${targetWeek}주차로 이동되었습니다.`, 'success');
        }
    }

    // Modal Management
    showAddScheduleModal(week) {
        document.getElementById('scheduleWeek').value = week;
        document.getElementById('scheduleTask').value = '';
        document.getElementById('scheduleResearcher').value = '';
        document.getElementById('scheduleProject').value = '';
        document.getElementById('schedulePriority').value = '보통';
        document.getElementById('scheduleNotes').value = '';
        
        const modal = new bootstrap.Modal(document.getElementById('addScheduleModal'));
        modal.show();
    }

    showEditScheduleModal(id) {
        // Find schedule
        let schedule = null;
        let week = null;
        
        for (let weekNum in this.schedules) {
            const found = this.schedules[weekNum].find(s => s.id === id);
            if (found) {
                schedule = found;
                week = weekNum;
                break;
            }
        }
        
        if (!schedule) return;
        
        // Populate form
        document.getElementById('editScheduleId').value = id;
        document.getElementById('editScheduleWeek').value = week;
        document.getElementById('editScheduleTask').value = schedule.task;
        document.getElementById('editScheduleResearcher').value = schedule.researcher || '';
        document.getElementById('editScheduleProject').value = schedule.project || '';
        document.getElementById('editSchedulePriority').value = schedule.priority || '보통';
        document.getElementById('editScheduleNotes').value = schedule.notes || '';
        
        const modal = new bootstrap.Modal(document.getElementById('editScheduleModal'));
        modal.show();
    }

    // Form Handlers
    async handleAddSchedule(e) {
        const formData = new FormData(e.target);
        const week = formData.get('week');
        const scheduleData = {
            task: formData.get('task'),
            researcher: formData.get('researcher'),
            project: formData.get('project'),
            priority: formData.get('priority'),
            notes: formData.get('notes')
        };
        
        try {
            await this.addSchedule(week, scheduleData);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addScheduleModal'));
            modal.hide();
            
            // Show success message
            this.showNotification('일정이 추가되었습니다.', 'success');
        } catch (error) {
            this.showNotification('일정 추가 중 오류가 발생했습니다.', 'error');
        }
    }

    async handleEditSchedule(e) {
        const formData = new FormData(e.target);
        const id = formData.get('id');
        const week = formData.get('week');
        const scheduleData = {
            task: formData.get('task'),
            researcher: formData.get('researcher'),
            project: formData.get('project'),
            priority: formData.get('priority'),
            notes: formData.get('notes')
        };
        
        try {
            await this.updateSchedule(id, week, scheduleData);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
            modal.hide();
            
            // Show success message
            this.showNotification('일정이 수정되었습니다.', 'success');
        } catch (error) {
            this.showNotification('일정 수정 중 오류가 발생했습니다.', 'error');
        }
    }

    async handleDeleteSchedule() {
        const id = document.getElementById('editScheduleId').value;
        
        if (confirm('정말로 이 일정을 삭제하시겠습니까?')) {
            try {
                await this.deleteSchedule(id);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editScheduleModal'));
                modal.hide();
                
                // Show success message
                this.showNotification('일정이 삭제되었습니다.', 'success');
            } catch (error) {
                this.showNotification('일정 삭제 중 오류가 발생했습니다.', 'error');
            }
        }
    }

    // Notifications
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeeklyScheduleManager();
});