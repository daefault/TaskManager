// static/js/project_tasks.js

let projectId = window.location.pathname.split('/')[2];
let currentPage = 1;
const limit = 10;
let currentSearchQuery = '';
let projectOwnerId = null; 
let currentUserId = parseInt(localStorage.getItem('user_id'));


document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    // Устанавливаем минимальную дату для дедлайна
    const now = new Date();
    now.setMinutes(now.getMinutes() + 1);
    const localDateTime = now.toISOString().slice(0, 16);
    document.getElementById('taskDeadline').setAttribute('min', localDateTime);

    loadProjectInfo();
    loadTasks();
    setUserName();
    updateUnreadCount();

    document.getElementById('logoutBtn').addEventListener('click', function() {
        // Показываем модалку вместо прямого выхода
        const modal = new bootstrap.Modal(document.getElementById('confirmLogoutModal'));
        modal.show();
    });
    document.getElementById('confirmLogoutBtn').addEventListener('click', function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        window.location.href = '/';
    });

    document.getElementById('createTaskBtn').addEventListener('click', function() {
        clearErrors();
        loadProjectMembersForTask();
        document.getElementById('createTaskForm').reset();
        const modal = new bootstrap.Modal(document.getElementById('createTaskModal'));
        modal.show();
    });

    document.getElementById('createTaskForm').addEventListener('submit', createTask);

    // ===== ПОИСК =====
    document.getElementById('searchTasksBtn').addEventListener('click', function() {
        const query = document.getElementById('searchTasksInput').value.trim();
        currentSearchQuery = query;
        currentPage = 1;
        loadTasks();
        document.getElementById('clearSearchTasksBtn').style.display = query ? 'inline-block' : 'none';
    });

    document.getElementById('searchTasksInput').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('searchTasksBtn').click();
        }
    });

    document.getElementById('clearSearchTasksBtn').addEventListener('click', function() {
        document.getElementById('searchTasksInput').value = '';
        currentSearchQuery = '';
        currentPage = 1;
        loadTasks();
        this.style.display = 'none';
    });

    // ===== ФИЛЬТРЫ =====
    document.getElementById('filterStatus').addEventListener('change', function() {
        currentPage = 1;
        loadTasks();
    });
    document.getElementById('filterPriority').addEventListener('change', function() {
        currentPage = 1;
        loadTasks();
    });
    document.getElementById('resetFiltersBtn').addEventListener('click', function() {
        document.getElementById('filterStatus').value = '';
        document.getElementById('filterPriority').value = '';
        document.getElementById('searchTasksInput').value = '';
        currentSearchQuery = '';
        currentPage = 1;
        document.getElementById('clearSearchTasksBtn').style.display = 'none';
        loadTasks();
    });
});

function setUserName() {
    const username = localStorage.getItem('username');
    const userNameElement = document.getElementById('userName');
    if (username && userNameElement) {
        userNameElement.textContent = username;
    }
}

// ========== ЗАГРУЗКА ПРОЕКТА ==========
async function loadProjectInfo() {
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}`);
        if (response.ok) {
            const project = await response.json();
            document.getElementById('projectTitle').textContent = `Задачи: ${project.name}`;
            projectOwnerId = project.owner_id;
        }
    } catch (error) {
        console.error('Ошибка загрузки проекта:', error);
    }
}

// ========== ЗАГРУЗКА ЗАДАЧ ==========
async function loadTasks() {
    const token = localStorage.getItem('access_token');
    const skip = (currentPage - 1) * limit;
    const status = document.getElementById('filterStatus').value;
    const priority = document.getElementById('filterPriority').value;
    const query = document.getElementById('searchTasksInput').value.trim();

    let url = `/api/tasks/?project_id=${projectId}&skip=${skip}&limit=${limit}`;
    if (status) url += `&status=${status}`;
    if (priority) url += `&priority=${priority}`;
    if (query) url += `&q=${encodeURIComponent(query)}`;

    try {
        const response = await fetchWithAuth(url);

        if (response.status === 401) {
            const refreshed = await refreshToken();
            if (refreshed) {
                loadTasks();
                return;
            } else {
                window.location.href = '/';
                return;
            }
        }

        if (!response.ok) throw new Error('Ошибка загрузки задач');

        const data = await response.json();
        displayTasks(data.items, data.total);
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('tasksList').innerHTML = `
            <div class="col-12 text-center py-5 text-danger">
                Не удалось загрузить задачи
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
    }
}

// ========== ОТОБРАЖЕНИЕ ЗАДАЧ ==========
function displayTasks(tasks, total) {
    const container = document.getElementById('tasksList');
    if (tasks.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted">
                    ${currentSearchQuery ? 'Задачи не найдены' : 'В этом проекте пока нет задач'}
                </p>
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }

    let html = '';
    tasks.forEach(task => {
        const isProjectOwner = projectOwnerId === currentUserId;
        const statusColors = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'done': 'success',
            'cancelled': 'danger',
            'overdue': 'danger'
        };
        const priorityLabels = {
            'low': 'Низкий',
            'medium': 'Средний',
            'high': 'Высокий',
            'critical': 'Критический'
        };

        html += `
            <div class="col-md-6 mb-3">
                <div class="card h-100 shadow-sm">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title text-truncate" style="max-width: 70%;" title="${task.title}">${task.title}</h5>
                            <div class="d-flex gap-1">
                                ${isProjectOwner ? '<span class="badge bg-warning text-dark">👑 Владелец</span>' : ''}
                                <span class="badge bg-${statusColors[task.status] || 'secondary'}">${translateStatus(task.status)}</span>
                            </div>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-2">
                            <span class="badge bg-${getPriorityColor(task.priority)}">
                                ${task.priority ? `Приоритет: ${translatePriority(task.priority)}` : ''}
                            </span>
                            <span class="text-muted small">Создана: ${new Date(task.created_at).toLocaleDateString()}</span>
                        </div>
                        ${task.deadline ? `<div class="mt-1"><small class="text-muted">Дедлайн: ${formatDate(task.deadline)}</small></div>` : ''}
                    </div>
                    <div class="card-footer bg-transparent">
                        <a href="/tasks/${task.id}" class="btn btn-outline-primary btn-sm w-100">
                            <i class="fas fa-eye me-1"></i>Подробнее
                        </a>
                    </div>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;

    renderPagination(total);
}


// ========== ПАГИНАЦИЯ ==========
function renderPagination(total) {
    const container = document.getElementById('paginationContainer');
    const totalPages = Math.ceil(total / limit);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHtml = `<nav><ul class="pagination">`;

    paginationHtml += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage - 1})">←</button>
        </li>
    `;

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        paginationHtml += `<li class="page-item"><button class="page-link" onclick="changePage(1)">1</button></li>`;
        if (startPage > 2) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <button class="page-link" onclick="changePage(${i})">${i}</button>
            </li>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHtml += `
            <li class="page-item"><button class="page-link" onclick="changePage(${totalPages})">${totalPages}</button></li>
        `;
    }

    paginationHtml += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage + 1})">→</button>
        </li>
    `;

    paginationHtml += `</ul></nav>`;
    container.innerHTML = paginationHtml;
}

function changePage(page) {
    currentPage = page;
    loadTasks();
    window.scrollTo(0, 0);
}

// ========== ЗАГРУЗКА УЧАСТНИКОВ ДЛЯ СОЗДАНИЯ ЗАДАЧИ ==========
async function loadProjectMembersForTask() {
    const token = localStorage.getItem('access_token');
    const container = document.getElementById('assigneesCheckboxes');
    container.innerHTML = '<p class="text-muted">Загрузка...</p>';

    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/members`);
        if (response.ok) {
            const members = await response.json();
            if (members.length === 0) {
                container.innerHTML = '<p class="text-muted">Нет участников для назначения</p>';
                return;
            }

            let html = '';
            members.forEach(member => {
                html += `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" value="${member.id}" id="assignee_${member.id}">
                        <label class="form-check-label" for="assignee_${member.id}">
                            ${member.username} (${member.email || 'нет email'})
                        </label>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-danger">Ошибка загрузки участников</p>';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        container.innerHTML = '<p class="text-danger">Ошибка соединения</p>';
    }
}

// ========== ОЧИСТКА ОШИБОК ==========
function clearErrors() {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
}

// ========== ПОКАЗ ОШИБОК ПОД ПОЛЯМИ ==========
function showFieldErrors(errorData) {
    clearErrors();

    if (errorData.detail && Array.isArray(errorData.detail)) {
        const errors = errorData.detail;

        errors.forEach(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            
            const fieldMap = {
                'title': { inputId: 'taskTitle', errorId: 'taskTitleError' },
                'description': { inputId: 'taskDescription', errorId: 'taskDescriptionError' },
                'priority': { inputId: 'taskPriority', errorId: 'taskPriorityError' },
                'deadline': { inputId: 'taskDeadline', errorId: 'taskDeadlineError' },
                'assignee_ids': { inputId: 'assigneesCheckboxes', errorId: 'assigneesError' }
            };

            const mapping = fieldMap[field];
            if (!mapping) return;

            const inputElement = document.getElementById(mapping.inputId);
            const errorElement = document.getElementById(mapping.errorId);

            if (inputElement) {
                inputElement.classList.add('is-invalid');
            }

            if (errorElement) {
                const userMessage = getUserFriendlyMessage(field, msg);
                errorElement.textContent = userMessage;
            }
        });
    }
}

// ========== ПРЕОБРАЗОВАНИЕ СООБЩЕНИЙ ==========
function getUserFriendlyMessage(field, msg) {
    const fieldNames = {
        'title': 'Название',
        'description': 'Описание',
        'deadline': 'Дедлайн',
        'status': 'Статус',
        'priority': 'Приоритет',
        'project_id': 'Проект',
        'assignee_ids': 'Исполнители'
    };

    if (msg.includes('String should have at least')) {
        const min = msg.match(/\d+/)?.[0] || '3';
        return `Минимум ${min} символов`;
    }
    if (msg.includes('String should have at most')) {
        const max = msg.match(/\d+/)?.[0] || '200';
        return `Максимум ${max} символов`;
    }
    if (msg.includes('field required')) {
        return 'Поле обязательно для заполнения';
    }
    if (msg.includes('value_error') && msg.includes('past')) {
        return 'Не может быть в прошлом';
    }
    if (msg.includes('value_error') && msg.includes('future')) {
        return 'Не может быть в будущем';
    }
    if (msg.includes('enum')) {
        return 'Выберите значение из списка';
    }
    return msg;
}

// ========== СОЗДАНИЕ ЗАДАЧИ ==========
async function createTask(event) {
    event.preventDefault();
    const token = localStorage.getItem('access_token');

    clearErrors();

    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDescription').value.trim();
    const priority = document.getElementById('taskPriority').value;
    const deadline = document.getElementById('taskDeadline').value;

    const assigneeIds = [];
    document.querySelectorAll('#assigneesCheckboxes input:checked').forEach(cb => {
        assigneeIds.push(parseInt(cb.value));
    });

    const data = {
        title,
        description,
        priority,
        project_id: parseInt(projectId),
        assignee_ids: assigneeIds
    };

    if (deadline) {
        data.deadline = new Date(deadline).toISOString();
    }

    try {
        const response = await fetchWithAuth('/api/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
            modal.hide();
            loadTasks();
            showToast('Задача создана!', 'success');
        } else if (response.status === 422) {
            const errorData = await response.json();
            showFieldErrors(errorData);
        } else {
            const errorData = await response.json();
            if (errorData.detail && errorData.detail.includes('уже существует')) {
                document.getElementById('taskTitle').classList.add('is-invalid');
                document.getElementById('taskTitleError').textContent = errorData.detail;
            } else {
                showToast('Ошибка: ' + (errorData.detail || 'Произошла ошибка'), 'error');
            }
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== ОБНОВЛЕНИЕ ТОКЕНА ==========
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
        const response = await fetchWithAuth('/api/auth/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            return true;
        }
        return false;
    } catch {
        return false;
    }
}

// ========== ТОСТ-УВЕДОМЛЕНИЯ ==========
function showToast(message, type = 'success') {
    const toastElement = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toastElement.querySelector('.toast-header');

    toastMessage.textContent = message;
    toastHeader.style.backgroundColor = type === 'success' ? '#d4edda' : '#f8d7da';
    toastHeader.style.color = type === 'success' ? '#155724' : '#721c24';

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}