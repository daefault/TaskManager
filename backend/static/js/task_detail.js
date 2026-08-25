// static/js/task_detail.js

const taskId = window.location.pathname.split('/').pop();
let currentTask = null;
let userIdToRemove = null;
const MAX_TASK_DESCRIPTION_LENGTH = 300;
let projectOwnerId = null;
// ===== КОММЕНТАРИИ (переменные) =====
let commentsSkip = 0;
const commentsLimit = 10;
let isLoadingComments = false;
let commentIdToDelete = null;

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    setUserName();
    loadTask();
    updateUnreadCount();

    // ===== ВЫХОД =====
    document.getElementById('logoutBtn').addEventListener('click', function() {
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

    // ===== СМЕНА СТАТУСА =====
    document.getElementById('changeTaskStatusBtn').addEventListener('click', function() {
        const currentStatus = document.getElementById('taskStatus').textContent;
        const statusSelect = document.getElementById('newTaskStatus');
        if (statusSelect) statusSelect.value = currentStatus;
        const modal = new bootstrap.Modal(document.getElementById('changeTaskStatusModal'));
        modal.show();
    });
    document.getElementById('changeTaskStatusForm').addEventListener('submit', changeTaskStatus);

    // ===== СМЕНА ПРИОРИТЕТА =====
    document.getElementById('changeTaskPriorityBtn').addEventListener('click', function() {
        const currentPriority = document.getElementById('taskPriority').textContent;
        const prioritySelect = document.getElementById('newTaskPriority');
        if (prioritySelect) prioritySelect.value = currentPriority;
        const modal = new bootstrap.Modal(document.getElementById('changeTaskPriorityModal'));
        modal.show();
    });
    document.getElementById('changeTaskPriorityForm').addEventListener('submit', changeTaskPriority);

    // ===== СМЕНА ДЕДЛАЙНА =====
    document.getElementById('changeTaskDeadlineBtn').addEventListener('click', function() {
        const currentDeadline = document.getElementById('taskDeadline').textContent;
        const deadlineInput = document.getElementById('newTaskDeadline');
        
        // 👇 Устанавливаем минимальную дату в ЛОКАЛЬНОМ времени
        const now = new Date();
        // Добавляем 1 минуту, чтобы можно было выбрать текущее время
        now.setMinutes(now.getMinutes() + 1);
        
        // 👇 Используем getLocalDateTime (без конвертации в UTC)
        const minLocal = getLocalDateTime(now);
        deadlineInput.setAttribute('min', minLocal);
        
        if (currentDeadline && currentDeadline !== 'Без дедлайна') {
            const utcDate = new Date(currentDeadline);
            // 👇 Конвертируем UTC в локальное время для отображения
            const localDate = new Date(utcDate.getTime() - utcDate.getTimezoneOffset() * 60000);
            if (localDate >= now) {
                deadlineInput.value = getLocalDateTime(localDate);
            } else {
                deadlineInput.value = '';
            }
        }
        const modal = new bootstrap.Modal(document.getElementById('changeTaskDeadlineModal'));
        modal.show();
    });
    document.getElementById('changeTaskDeadlineForm').addEventListener('submit', changeTaskDeadline);

    // ===== УДАЛЕНИЕ ЗАДАЧИ =====
    document.getElementById('deleteTaskBtn').addEventListener('click', function() {
        const taskName = document.getElementById('taskTitle').textContent;
        document.getElementById('deleteTaskName').textContent = taskName;
        const modal = new bootstrap.Modal(document.getElementById('confirmDeleteTaskModal'));
        modal.show();
    });

    document.getElementById('confirmDeleteTaskBtn').addEventListener('click', function() {
        deleteTask();
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteTaskModal'));
        if (modal) modal.hide();
    });

    // ===== ИСПОЛНИТЕЛИ =====
    document.getElementById('addAssigneeBtn').addEventListener('click', function() {
        document.getElementById('searchAssigneeInput').value = '';
        document.getElementById('searchResultsList').innerHTML = '<p class="text-muted">Введите минимум 2 символа для поиска...</p>';
        loadProjectMembersForSearch();
        const modal = new bootstrap.Modal(document.getElementById('addAssigneeModal'));
        modal.show();
    });

    document.getElementById('searchAssigneeInput').addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length < 2) {
            document.getElementById('searchResultsList').innerHTML = '<p class="text-muted">Введите минимум 2 символа...</p>';
            return;
        }
        searchMembersToAdd(query);
    });

    document.getElementById('confirmRemoveAssigneeBtn').addEventListener('click', function() {
        if (userIdToRemove !== null) {
            removeAssignee(userIdToRemove);
            userIdToRemove = null;
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmRemoveAssigneeModal'));
            if (modal) modal.hide();
        }
    });

    // ===== INLINE EDITING =====
    const titleEl = document.getElementById('taskTitle');
    if (titleEl) {
        titleEl.addEventListener('blur', function() {
            saveTaskInlineEdit('title', this.textContent.trim());
        });
        titleEl.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.blur();
            }
        });
    }

    const descEl = document.getElementById('taskDescription');
    if (descEl) {
        descEl.addEventListener('blur', function() {
            saveTaskInlineEdit('description', this.textContent.trim());
        });
    }

    document.getElementById('toggleTaskDescriptionBtn')?.addEventListener('click', function() {
        const descEl = document.getElementById('taskDescription');
        const isExpanded = this.dataset.expanded === 'true';

        if (isExpanded) {
            descEl.textContent = this.dataset.fullText.slice(0, MAX_TASK_DESCRIPTION_LENGTH) + '...';
            this.textContent = 'Развернуть';
            this.dataset.expanded = 'false';
        } else {
            descEl.textContent = this.dataset.fullText;
            this.textContent = 'Свернуть';
            this.dataset.expanded = 'true';
        }
    });

    // ===== КОММЕНТАРИИ =====
    document.getElementById('addCommentForm').addEventListener('submit', addComment);
    document.getElementById('loadMoreCommentsBtn')?.addEventListener('click', function() {
        loadComments(false);
    });
});

// ========== ДЕЛЕГИРОВАНИЕ ДЛЯ УДАЛЕНИЯ ИСПОЛНИТЕЛЕЙ ==========
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-assignee-btn')) {
        const userId = parseInt(e.target.dataset.userId);
        const username = e.target.dataset.username;
        userIdToRemove = userId;
        document.getElementById('removeAssigneeName').textContent = username;
        const modal = new bootstrap.Modal(document.getElementById('confirmRemoveAssigneeModal'));
        modal.show();
    }
});


// ========== УСТАНОВКА ИМЕНИ ==========
function setUserName() {
    const username = localStorage.getItem('username');
    const userNameElement = document.getElementById('userName');
    if (username && userNameElement) {
        userNameElement.textContent = username;
    }
}

// ========== ЗАГРУЗКА ЗАДАЧИ ==========
async function loadTask() {
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`);

        if (response.status === 404) {
            document.getElementById('loadingIndicator').innerHTML = `
                <div class="alert alert-danger">Задача не найдена</div>
            `;
            return;
        }

        if (response.status === 403) {
            document.getElementById('loadingIndicator').innerHTML = `
                <div class="alert alert-danger">У вас нет доступа к этой задаче</div>
            `;
            return;
        }

        if (!response.ok) throw new Error('Ошибка загрузки задачи');

        const task = await response.json();
        currentTask = task;
        const projectResponse = await fetchWithAuth(`/api/projects/${task.project_id}`);
        if (projectResponse.ok) {
            const project = await projectResponse.json();
            projectOwnerId = project.owner_id;
        }
        displayTask(task);
        loadAssignees();
        loadComments(true);
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('loadingIndicator').innerHTML = `
            <div class="alert alert-danger">Не удалось загрузить задачу</div>
        `;
    }
}

// ========== ОТОБРАЖЕНИЕ ЗАДАЧИ ==========
function displayTask(task) {
    document.getElementById('loadingIndicator').classList.add('d-none');
    document.getElementById('taskDetail').classList.remove('d-none');

    const titleEl = document.getElementById('taskTitle');
    const descEl = document.getElementById('taskDescription');
    const toggleBtn = document.getElementById('toggleTaskDescriptionBtn');

    const currentUserId = parseInt(localStorage.getItem('user_id'));
    const isCreator = task.creator_id === currentUserId;

    titleEl.textContent = task.title;
    titleEl.contentEditable = isCreator ? 'true' : 'false';
    titleEl.style.wordWrap = 'break-word';
    titleEl.style.overflowWrap = 'break-word';
    titleEl.style.maxWidth = '100%';

    descEl.contentEditable = isCreator ? 'true' : 'false';
    descEl.style.wordWrap = 'break-word';
    descEl.style.overflowWrap = 'break-word';
    descEl.style.whiteSpace = 'pre-wrap';
    descEl.style.wordBreak = 'break-word';
    descEl.style.maxWidth = '100%';

    if (task.description && task.description.length > MAX_TASK_DESCRIPTION_LENGTH) {
        descEl.textContent = task.description.slice(0, MAX_TASK_DESCRIPTION_LENGTH) + '...';
        toggleBtn.classList.remove('d-none');
        toggleBtn.textContent = 'Развернуть';
        toggleBtn.dataset.fullText = task.description;
        toggleBtn.dataset.expanded = 'false';
    } else {
        descEl.textContent = task.description || 'Без описания';
        toggleBtn.classList.add('d-none');
    }

    const statusBadge = document.getElementById('taskStatus');
    statusBadge.textContent = translateStatus(task.status);
    statusBadge.className = `badge bg-${getStatusColor(task.status)}`;

    document.getElementById('taskPriority').textContent = `Приоритет: ${translatePriority(task.priority)}`;
    document.getElementById('taskDeadline').textContent = task.deadline ? formatDate(task.deadline) : 'Без дедлайна';

    const creatorBadge = document.getElementById('taskCreator');
    if (task.creator && task.creator.username) {
        creatorBadge.textContent = `Создатель: ${task.creator.username}`;
    } else {
        creatorBadge.textContent = `Создатель: ${task.creator_id}`;
    }
}

// ========== СМЕНА СТАТУСА ==========
async function changeTaskStatus(event) {
    event.preventDefault();
    const newStatus = document.getElementById('newTaskStatus').value;
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeTaskStatusModal'));
            if (modal) modal.hide();
            loadTask();
            showToast(`Статус изменен на "${translateStatus(newStatus)}"`, 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось изменить статус'), 'error');
        }
    } catch (error) {
        console.error('Ошибка смены статуса:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== СМЕНА ПРИОРИТЕТА ==========
async function changeTaskPriority(event) {
    event.preventDefault();
    const newPriority = document.getElementById('newTaskPriority').value;
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify({ priority: newPriority })
        });
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeTaskPriorityModal'));
            if (modal) modal.hide();
            loadTask();
            showToast(`Приоритет изменен на "${translatePriority(newPriority)}"`, 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось изменить приоритет'), 'error');
        }
    } catch (error) {
        console.error('Ошибка смены приоритета:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== СМЕНА ДЕДЛАЙНА ==========
async function changeTaskDeadline(event) {
    event.preventDefault();
    const newDeadline = document.getElementById('newTaskDeadline').value;

    if (newDeadline) {
        // 👇 Парсим в локальном времени
        const selectedDate = new Date(newDeadline);
        const now = new Date();
        now.setSeconds(0, 0);
        
        // 👇 Сравниваем в локальном времени
        if (selectedDate < now) {
            showToast('Дедлайн не может быть в прошлом', 'error');
            return;
        }
    }

    // 👇 Отправляем на сервер в UTC
    const data = { 
        deadline: newDeadline ? new Date(newDeadline).toISOString() : null 
    };
    
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeTaskDeadlineModal'));
            if (modal) modal.hide();
            loadTask();
            showToast('Дедлайн обновлен!', 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось изменить дедлайн'), 'error');
        }
    } catch (error) {
        console.error('Ошибка смены дедлайна:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== INLINE EDITING ==========
async function saveTaskInlineEdit(field, value) {
    const task = currentTask;
    if (!task) return;

    const data = {};
    const titleEl = document.getElementById('taskTitle');
    const descEl = document.getElementById('taskDescription');
    const toggleBtn = document.getElementById('toggleTaskDescriptionBtn');

    if (field === 'title') {
        if (value === task.title || !value) {
            titleEl.textContent = task.title;
            return;
        }
        if (value.length > 40) {
            showToast('Название не может превышать 40 символов', 'error');
            titleEl.textContent = task.title;
            return;
        }
        data.title = value;
    } else if (field === 'description') {
        if (value === (task.description || '')) return;
        data.description = value || null;
    }

    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const updated = await response.json();
            currentTask = updated;
            titleEl.textContent = updated.title;

            descEl.style.wordWrap = 'break-word';
            descEl.style.overflowWrap = 'break-word';
            descEl.style.whiteSpace = 'pre-wrap';
            descEl.style.wordBreak = 'break-word';
            descEl.style.maxWidth = '100%';

            if (updated.description && updated.description.length > MAX_TASK_DESCRIPTION_LENGTH) {
                descEl.textContent = updated.description.slice(0, MAX_TASK_DESCRIPTION_LENGTH) + '...';
                toggleBtn.classList.remove('d-none');
                toggleBtn.textContent = 'Развернуть';
                toggleBtn.dataset.fullText = updated.description;
                toggleBtn.dataset.expanded = 'false';
            } else {
                descEl.textContent = updated.description || 'Без описания';
                toggleBtn.classList.add('d-none');
            }

            showToast(field === 'title' ? 'Название обновлено!' : 'Описание обновлено!', 'success');
        } else {
            const error = await response.json();
            const errorMessage = getTaskErrorMessage(error);
            showToast('Ошибка: ' + errorMessage, 'error');
            if (field === 'title') titleEl.textContent = task.title;
            else descEl.textContent = task.description || 'Без описания';
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        showToast('Ошибка соединения с сервером', 'error');
        if (field === 'title') titleEl.textContent = task.title;
        else descEl.textContent = task.description || 'Без описания';
    }
}

function getTaskErrorMessage(errorData) {
    if (errorData.detail && Array.isArray(errorData.detail)) {
        const errors = errorData.detail;
        const messages = errors.map(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            const fieldNames = { 'title': 'Название', 'description': 'Описание' };
            const fieldName = fieldNames[field] || field;
            if (msg.includes('String should have at least')) {
                const min = msg.match(/\d+/)?.[0] || '3';
                return `Минимальная длина ${min} символов`;
            }
            if (msg.includes('String should have at most')) {
                const max = msg.match(/\d+/)?.[0] || '40';
                return `Максимальная длина ${max} символов`;
            }
            if (msg.includes('field required')) return 'Поле обязательно для заполнения';
            if (msg.includes('уже существует')) return 'Задача с таким названием уже существует';
            if (msg.includes('value_error') && msg.includes('past')) return 'Не может быть в прошлом';
            return msg;
        });
        return messages.join('; ');
    }
    return errorData.detail || 'Ошибка валидации';
}

// ========== КОММЕНТАРИИ (с пагинацией) ==========
async function loadComments(reset = true) {
    if (isLoadingComments) return;
    isLoadingComments = true;

    if (reset) {
        commentsSkip = 0;
        document.getElementById('commentsList').innerHTML = '<p class="text-muted">Загрузка комментариев...</p>';
        document.getElementById('commentsPagination').classList.add('d-none');
    }

    try {
        const response = await fetchWithAuth(
            `/api/comments/task/${taskId}?skip=${commentsSkip}&limit=${commentsLimit}`
        );

        if (response.ok) {
            const comments = await response.json();
            
            if (reset) {
                displayComments(comments);
            } else {
                appendComments(comments);
            }

            const hasMore = comments.length === commentsLimit;
            if (hasMore) {
                document.getElementById('commentsPagination').classList.remove('d-none');
            } else {
                document.getElementById('commentsPagination').classList.add('d-none');
            }

            commentsSkip += comments.length;
        } else {
            document.getElementById('commentsList').innerHTML = `
                <p class="text-danger">Не удалось загрузить комментарии</p>
            `;
        }
    } catch (error) {
        console.error('Ошибка загрузки комментариев:', error);
        document.getElementById('commentsList').innerHTML = `
            <p class="text-danger">Ошибка загрузки комментариев</p>
        `;
    } finally {
        isLoadingComments = false;
    }
}

function displayComments(comments) {
    const container = document.getElementById('commentsList');
    if (!comments || comments.length === 0) {
        container.innerHTML = '<p class="text-muted">Нет комментариев. Будьте первым!</p>';
        document.getElementById('commentsPagination').classList.add('d-none');
        return;
    }

    container.innerHTML = buildCommentsHtml(comments);
}

function appendComments(comments) {
    const container = document.getElementById('commentsList');
    if (!comments || comments.length === 0) return;

    if (container.innerHTML.includes('Нет комментариев')) {
        container.innerHTML = '';
    }

    container.innerHTML += buildCommentsHtml(comments);
}

function buildCommentsHtml(comments) {
    const currentUserId = parseInt(localStorage.getItem('user_id'));
    let html = '';

    comments.forEach(comment => {
        const isAuthor = comment.author_id === currentUserId;
        const isProjectOwner = projectOwnerId === currentUserId;
        const canDelete = isAuthor || isProjectOwner;

        const username = comment.author?.username || 'Пользователь';
        const date = new Date(comment.created_at);
        const formattedDate = date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        html += `
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${username}</strong>
                        <span class="text-muted small ms-2">${formattedDate}</span>
                    </div>
                    ${canDelete ? `<button class="btn btn-sm btn-danger delete-comment-btn" data-comment-id="${comment.id}">✕</button>` : ''}
                </div>
                <p class="mb-0 mt-1" style="word-wrap: break-word; white-space: pre-wrap;">${comment.content}</p>
            </div>
        `;
    });

    return html;
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-comment-btn')) {
        commentIdToDelete = parseInt(e.target.dataset.commentId);
        const modal = new bootstrap.Modal(document.getElementById('confirmDeleteCommentModal'));
        modal.show();
    }
});

document.getElementById('confirmDeleteCommentBtn').addEventListener('click', function() {
    if (commentIdToDelete !== null) {
        deleteComment(commentIdToDelete);
        commentIdToDelete = null;
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteCommentModal'));
        if (modal) modal.hide();
    }
});


async function addComment(event) {
    event.preventDefault();

    const content = document.getElementById('commentContent').value.trim();
    if (!content) {
        showToast('Введите текст комментария', 'error');
        return;
    }

    if (content.length > 2000) {
        showToast('Комментарий не может превышать 2000 символов', 'error');
        return;
    }

    try {
        const response = await fetchWithAuth('/api/comments/', {
            method: 'POST',
            body: JSON.stringify({
                content: content,
                task_id: parseInt(taskId)
            })
        });

        if (response.ok) {
            document.getElementById('commentContent').value = '';
            loadComments(true);
            showToast('Комментарий добавлен!', 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось добавить комментарий'), 'error');
        }
    } catch (error) {
        console.error('Ошибка добавления комментария:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

async function deleteComment(commentId) {
    try {
        const response = await fetchWithAuth(`/api/comments/${commentId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadComments(true);
            showToast('Комментарий удален!', 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось удалить комментарий'), 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления комментария:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== ЗАГРУЗКА ИСПОЛНИТЕЛЕЙ ==========
async function loadAssignees() {
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}/assignees`);
        if (response.ok) {
            const assignees = await response.json();
            displayAssignees(assignees);
        }
    } catch (error) {
        console.error('Ошибка загрузки исполнителей:', error);
    }
}

function displayAssignees(assignees) {
    const container = document.getElementById('assigneesList');
    if (!assignees || assignees.length === 0) {
        container.innerHTML = '<p class="text-muted">Нет исполнителей</p>';
        return;
    }

    let html = '<ul class="list-group">';
    assignees.forEach(assignee => {
        const username = assignee.username || 'Без имени';
        const email = assignee.email || 'нет email';
        html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${username} (${email})
                <button class="btn btn-sm btn-danger remove-assignee-btn" data-user-id="${assignee.id}" data-username="${username}">✕</button>
            </li>
        `;
    });
    html += '</ul>';
    container.innerHTML = html;
}

// ========== ЗАГРУЗКА УЧАСТНИКОВ ПРОЕКТА ==========
let projectMembers = [];

async function loadProjectMembersForSearch() {
    const projectId = currentTask?.project_id;
    if (!projectId) return;

    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/members`);
        if (response.ok) {
            projectMembers = await response.json();
        }
    } catch (error) {
        console.error('Ошибка загрузки участников проекта:', error);
    }
}

function searchMembersToAdd(query) {
    const container = document.getElementById('searchResultsList');
    
    const filtered = projectMembers.filter(member => 
        member.username.toLowerCase().includes(query.toLowerCase()) ||
        (member.email && member.email.toLowerCase().includes(query.toLowerCase()))
    );

    const currentAssigneeIds = getCurrentAssigneeIds();

    let html = '<div class="list-group">';
    let found = false;

    filtered.forEach(member => {
        if (currentAssigneeIds.includes(member.id)) return;
        found = true;
        html += `
            <button class="list-group-item list-group-item-action d-flex justify-content-between align-items-center add-assignee-btn" 
                    data-user-id="${member.id}" data-username="${member.username}">
                ${member.username} (${member.email || 'нет email'})
                <span class="badge bg-primary">Добавить</span>
            </button>
        `;
    });

    if (!found) {
        if (filtered.length === 0) {
            html = '<p class="text-muted">Пользователи не найдены в проекте</p>';
        } else {
            html = '<p class="text-muted">Все участники проекта уже являются исполнителями</p>';
        }
    } else {
        html += '</div>';
    }

    container.innerHTML = html;

    container.querySelectorAll('.add-assignee-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = parseInt(this.dataset.userId);
            const username = this.dataset.username;
            addAssignee(userId, username);
        });
    });
}

function getCurrentAssigneeIds() {
    const items = document.querySelectorAll('#assigneesList .list-group-item');
    const ids = [];
    items.forEach(item => {
        const button = item.querySelector('.remove-assignee-btn');
        if (button) {
            ids.push(parseInt(button.dataset.userId));
        }
    });
    return ids;
}

// ========== ДОБАВЛЕНИЕ ИСПОЛНИТЕЛЯ ==========
async function addAssignee(userId, username) {
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}/assignees/${userId}`, {
            method: 'POST'
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addAssigneeModal'));
            if (modal) modal.hide();
            loadAssignees();
            showToast(`Исполнитель "${username}" добавлен!`, 'success');
        } else {
            const error = await response.json();
            if (error.detail && error.detail.includes('уже является исполнителем')) {
                document.getElementById('searchResultsList').innerHTML = `<p class="text-danger">${error.detail}</p>`;
            } else {
                showToast('Ошибка: ' + (error.detail || 'Не удалось добавить исполнителя'), 'error');
            }
        }
    } catch (error) {
        console.error('Ошибка добавления:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== УДАЛЕНИЕ ИСПОЛНИТЕЛЯ ==========
async function removeAssignee(userId) {
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}/assignees/${userId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadAssignees();
            showToast('Исполнитель удален!', 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось удалить исполнителя'), 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== УДАЛЕНИЕ ЗАДАЧИ ==========
async function deleteTask() {
    try {
        const response = await fetchWithAuth(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const projectId = currentTask?.project_id;
            if (projectId) {
                window.location.href = `/projects/${projectId}/tasks`;
            } else {
                window.location.href = '/projects';
            }
        } else {
            const errorData = await response.json();
            showToast('Ошибка: ' + (errorData.detail || 'Не удалось удалить задачу'), 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showToast('Ошибка соединения с сервером', 'error');
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

function getLocalDateTime(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}