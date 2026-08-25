// static/js/project_detail.js

let projectId = window.location.pathname.split('/').pop();
let userIdToRemove = null;
let currentUserId = null;
const MAX_DESCRIPTION_LENGTH = 300;

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    currentUserId = parseInt(localStorage.getItem('user_id'));
    setUserName();

    document.getElementById('tasksLink').href = `/projects/${projectId}/tasks`;

    loadProject();
    loadMembers();
    updateUnreadCount();

    // ===== КНОПКИ =====
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

    const changeStatusBtn = document.getElementById('changeStatusBtn');
    if (changeStatusBtn) {
        changeStatusBtn.addEventListener('click', function() {
            const currentStatus = document.getElementById('projectStatus').textContent;
            const statusSelect = document.getElementById('newProjectStatus');
            if (statusSelect) statusSelect.value = currentStatus;
            const modal = new bootstrap.Modal(document.getElementById('changeStatusModal'));
            modal.show();
        });
    }

    document.getElementById('changeStatusForm')?.addEventListener('submit', changeStatus);

    document.getElementById('deleteProjectBtn').addEventListener('click', function() {
        const projectName = document.getElementById('projectName').textContent;
        document.getElementById('deleteProjectName').textContent = projectName;
        const modal = new bootstrap.Modal(document.getElementById('confirmDeleteProjectModal'));
        modal.show();
    });

    document.getElementById('confirmDeleteProjectBtn').addEventListener('click', function() {
        deleteProject();
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteProjectModal'));
        if (modal) modal.hide();
    });

    document.getElementById('addMemberBtn').addEventListener('click', function() {
        document.getElementById('searchUserInput').value = '';
        document.getElementById('searchResults').innerHTML = '';
        const modal = new bootstrap.Modal(document.getElementById('addMemberModal'));
        modal.show();
    });

    document.getElementById('leaveProjectBtn').addEventListener('click', function() {
        const projectName = this.dataset.projectName;
        document.getElementById('leaveProjectName').textContent = projectName;
        const modal = new bootstrap.Modal(document.getElementById('confirmLeaveProjectModal'));
        modal.show();
    });

    document.getElementById('confirmLeaveProjectBtn').addEventListener('click', function() {
        leaveProject();
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmLeaveProjectModal'));
        if (modal) modal.hide();
    });

    // ===== INLINE EDITING =====
    const nameEl = document.getElementById('projectName');
    const descEl = document.getElementById('projectDescription');

    if (nameEl) {
        nameEl.addEventListener('blur', function() {
            saveInlineEdit('name', this.textContent.trim());
        });
        nameEl.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.blur();
            }
        });
    }

    if (descEl) {
        descEl.addEventListener('blur', function() {
            saveInlineEdit('description', this.textContent.trim());
        });
    }

    // ===== КНОПКА РАЗВЕРНУТЬ/СВЕРНУТЬ =====
    document.getElementById('toggleDescriptionBtn')?.addEventListener('click', function() {
        const descEl = document.getElementById('projectDescription');
        const isExpanded = this.dataset.expanded === 'true';

        if (isExpanded) {
            descEl.textContent = this.dataset.fullText.slice(0, MAX_DESCRIPTION_LENGTH) + '...';
            this.textContent = 'Развернуть';
            this.dataset.expanded = 'false';
        } else {
            descEl.textContent = this.dataset.fullText;
            this.textContent = 'Свернуть';
            this.dataset.expanded = 'true';
        }
    });

    // ===== ФИКС МОДАЛОК =====
    const modals = [
        'confirmRemoveMemberModal',
        'confirmDeleteProjectModal',
        'confirmLeaveProjectModal',
        'addMemberModal',
        'changeStatusModal'
    ];

    modals.forEach(id => {
        const modalElement = document.getElementById(id);
        if (modalElement) {
            modalElement.addEventListener('hidden.bs.modal', function() {
                document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                document.body.classList.remove('modal-open');
            });
        }
    });
});

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
function setUserName() {
    const username = localStorage.getItem('username');
    const userNameElement = document.getElementById('userName');
    if (username && userNameElement) {
        userNameElement.textContent = username;
    }
}

// ===== ДЕЛЕГИРОВАНИЕ ДЛЯ УДАЛЕНИЯ УЧАСТНИКА =====
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-member')) {
        const userId = parseInt(e.target.dataset.userId);
        const username = e.target.closest('li').querySelector('div').textContent.trim().split('(')[0].trim();
        userIdToRemove = userId;
        document.getElementById('removeMemberName').textContent = username;
        const modal = new bootstrap.Modal(document.getElementById('confirmRemoveMemberModal'));
        modal.show();
    }
});

document.getElementById('confirmRemoveMemberBtn').addEventListener('click', function() {
    if (userIdToRemove !== null) {
        removeMember(userIdToRemove);
        userIdToRemove = null;
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmRemoveMemberModal'));
        if (modal) modal.hide();
    }
});

// ===== ЗАГРУЗКА ПРОЕКТА =====
async function loadProject() {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}`);

        if (response.status === 404) {
            document.getElementById('loadingIndicator').innerHTML = `
                <div class="alert alert-danger">Проект не найден</div>
            `;
            return;
        }

        if (!response.ok) throw new Error('Ошибка загрузки проекта');

        const project = await response.json();
        displayProject(project);
        loadMembers();
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('loadingIndicator').innerHTML = `
            <div class="alert alert-danger">Не удалось загрузить проект</div>
        `;
    }
}

function displayProject(project) {
    document.getElementById('loadingIndicator').classList.add('d-none');
    document.getElementById('projectDetail').classList.remove('d-none');

    const isOwner = project.owner_id === currentUserId;
    const nameEl = document.getElementById('projectName');
    const descEl = document.getElementById('projectDescription');
    const toggleBtn = document.getElementById('toggleDescriptionBtn');

    nameEl.textContent = project.name;
    nameEl.contentEditable = isOwner ? 'true' : 'false';
    nameEl.style.wordWrap = 'break-word';
    nameEl.style.overflowWrap = 'break-word';

    // Описание с переносом
    descEl.contentEditable = isOwner ? 'true' : 'false';
    descEl.style.wordWrap = 'break-word';
    descEl.style.overflowWrap = 'break-word';
    descEl.style.whiteSpace = 'pre-wrap';
    descEl.style.wordBreak = 'break-word';
    descEl.style.maxWidth = '100%';

    if (project.description && project.description.length > MAX_DESCRIPTION_LENGTH) {
        descEl.textContent = project.description.slice(0, MAX_DESCRIPTION_LENGTH) + '...';
        toggleBtn.classList.remove('d-none');
        toggleBtn.textContent = 'Развернуть';
        toggleBtn.dataset.fullText = project.description;
        toggleBtn.dataset.expanded = 'false';
    } else {
        descEl.textContent = project.description || 'Без описания';
        toggleBtn.classList.add('d-none');
    }

    const statusBadge = document.getElementById('projectStatus');
        statusBadge.textContent = translateStatus(project.status);
        statusBadge.className = `badge bg-${getStatusColor(project.status)}`;

    window.currentProject = project;

    document.getElementById('changeStatusBtn').style.display = isOwner ? 'inline-block' : 'none';
    document.getElementById('deleteProjectBtn').style.display = isOwner ? 'inline-block' : 'none';
    document.getElementById('addMemberBtn').style.display = isOwner ? 'inline-block' : 'none';

    const leaveBtn = document.getElementById('leaveProjectBtn');
    if (isOwner) {
        leaveBtn.style.display = 'none';
    } else {
        leaveBtn.style.display = 'inline-block';
        leaveBtn.dataset.projectName = project.name;
    }
}

// ===== УЧАСТНИКИ =====
async function loadMembers() {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/members`);
        if (response.ok) {
            const members = await response.json();
            window.currentMembers = members;
            if (window.currentProject) {
                displayMembers(members, window.currentProject.owner_id);
            }
        }
    } catch (error) {
        console.error('Ошибка загрузки участников:', error);
    }
}

function displayMembers(members, ownerId) {
    const container = document.getElementById('membersList');
    if (members.length === 0) {
        container.innerHTML = '<p class="text-muted">Нет участников</p>';
        return;
    }

    const isOwner = ownerId === currentUserId;

    let html = '<ul class="list-group">';
    members.forEach(member => {
        const isOwnerUser = member.id === ownerId;
        const username = member.username || member.name || 'Без имени';
        const email = member.email || 'нет email';
        html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    ${username} (${email})
                    ${isOwnerUser ? ' <span class="badge bg-warning text-dark">👑 Владелец</span>' : ''}
                </div>
                ${!isOwnerUser && isOwner ? `<button class="btn btn-sm btn-danger remove-member" data-user-id="${member.id}" data-username="${username}">✕</button>` : ''}
            </li>
        `;
    });
    html += '</ul>';
    container.innerHTML = html;

    if (isOwner) {
        document.querySelectorAll('.remove-member').forEach(button => {
            button.addEventListener('click', function() {
                const userId = parseInt(this.dataset.userId);
                const username = this.dataset.username;
                userIdToRemove = userId;
                document.getElementById('removeMemberName').textContent = username;
                const modal = new bootstrap.Modal(document.getElementById('confirmRemoveMemberModal'));
                modal.show();
            });
        });
    }
}

// ===== INLINE EDITING =====
async function saveInlineEdit(field, value) {
    const project = window.currentProject;
    if (!project) return;

    const data = {};
    const nameEl = document.getElementById('projectName');
    const descEl = document.getElementById('projectDescription');
    const toggleBtn = document.getElementById('toggleDescriptionBtn');

    if (field === 'name') {
        if (value === project.name || !value) {
            nameEl.textContent = project.name;
            return;
        }
        if (value.length > 40) {
            showToast('Название не может превышать 40 символов', 'error');
            nameEl.textContent = project.name;
            return;
        }
        data.name = value;
    } else if (field === 'description') {
        if (value === (project.description || '')) return;
        data.description = value || null;
    }

    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const updated = await response.json();
            window.currentProject = updated;
            nameEl.textContent = updated.name;

            // Обновляем описание с переносом
            descEl.style.wordWrap = 'break-word';
            descEl.style.overflowWrap = 'break-word';
            descEl.style.whiteSpace = 'pre-wrap';
            descEl.style.wordBreak = 'break-word';
            descEl.style.maxWidth = '100%';

            if (updated.description && updated.description.length > MAX_DESCRIPTION_LENGTH) {
                descEl.textContent = updated.description.slice(0, MAX_DESCRIPTION_LENGTH) + '...';
                toggleBtn.classList.remove('d-none');
                toggleBtn.textContent = 'Развернуть';
                toggleBtn.dataset.fullText = updated.description;
                toggleBtn.dataset.expanded = 'false';
            } else {
                descEl.textContent = updated.description || 'Без описания';
                toggleBtn.classList.add('d-none');
            }

            showToast(field === 'name' ? 'Название обновлено!' : 'Описание обновлено!', 'success');
            localStorage.setItem('projectsNeedsRefresh', 'true');
        } else {
            const error = await response.json();
            const errorMessage = getInlineErrorMessage(error);
            showToast('Ошибка: ' + errorMessage, 'error');
            if (field === 'name') nameEl.textContent = project.name;
            else descEl.textContent = project.description || 'Без описания';
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        showToast('Ошибка соединения с сервером', 'error');
        if (field === 'name') nameEl.textContent = project.name;
        else descEl.textContent = project.description || 'Без описания';
    }
}

function getInlineErrorMessage(errorData) {
    if (errorData.detail && Array.isArray(errorData.detail)) {
        const errors = errorData.detail;
        const messages = errors.map(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            const fieldNames = { 'name': 'Название', 'description': 'Описание' };
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
            return msg;
        });
        return messages.join('; ');
    }
    return errorData.detail || 'Ошибка валидации';
}

// ===== СМЕНА СТАТУСА =====
async function changeStatus(event) {
    event.preventDefault();
    const newStatus = document.getElementById('newProjectStatus').value;

    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}`, {
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('changeStatusModal'));
            if (modal) modal.hide();
            loadProject();
            showToast(`Статус изменен на "${newStatus === 'active' ? 'Активный' : 'Архивный'}"`, 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось изменить статус'), 'error');
        }
    } catch (error) {
        console.error('Ошибка смены статуса:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ===== УДАЛЕНИЕ ПРОЕКТА =====
async function deleteProject() {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}`, { method: 'DELETE' });
        if (response.ok) {
            window.location.href = '/projects';
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось удалить проект'), 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ===== ПОКИНУТЬ ПРОЕКТ =====
async function leaveProject() {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/leave`, { method: 'POST' });
        if (response.ok) {
            window.location.href = '/projects';
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось покинуть проект'), 'error');
        }
    } catch (error) {
        console.error('Ошибка выхода из проекта:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ===== ПОИСК ПОЛЬЗОВАТЕЛЕЙ =====
let searchTimeout;

document.getElementById('searchUserInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value.trim();
    if (query.length < 2) {
        document.getElementById('searchResults').innerHTML = '';
        return;
    }
    searchTimeout = setTimeout(() => searchUsers(query), 300);
});

async function searchUsers(query) {
    try {
        const response = await fetchWithAuth(`/api/users/search?query=${encodeURIComponent(query)}`);
        if (response.ok) {
            const users = await response.json();
            displaySearchResults(users);
        } else {
            const error = await response.json();
            document.getElementById('searchResults').innerHTML = `<p class="text-danger mt-2">Ошибка: ${error.detail || 'Неизвестная ошибка'}</p>`;
        }
    } catch (error) {
        console.error('Ошибка поиска:', error);
        document.getElementById('searchResults').innerHTML = '<p class="text-danger mt-2">Ошибка соединения с сервером</p>';
    }
}

function displaySearchResults(users) {
    const container = document.getElementById('searchResults');
    if (users.length === 0) {
        container.innerHTML = '<p class="text-muted mt-2">Пользователи не найдены</p>';
        return;
    }

    const currentMembers = window.currentMembers || [];
    const memberIds = currentMembers.map(m => m.id);

    let html = '<div class="list-group">';
    let found = false;
    users.forEach(user => {
        if (memberIds.includes(user.id)) return;
        found = true;
        html += `
            <button class="list-group-item list-group-item-action d-flex justify-content-between align-items-center add-member-btn"
                    data-user-id="${user.id}" data-username="${user.username}">
                ${user.username} (${user.email || 'нет email'})
                <span class="badge bg-primary">Добавить</span>
            </button>
        `;
    });
    if (!found) {
        html = '<p class="text-muted mt-2">Все найденные пользователи уже в проекте</p>';
    }
    html += '</div>';
    container.innerHTML = html;

    container.querySelectorAll('.add-member-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = parseInt(this.dataset.userId);
            const username = this.dataset.username;
            addMember(userId, username);
        });
    });
}

async function addMember(userId, username) {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/members/${userId}`, { method: 'POST' });
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addMemberModal'));
            if (modal) modal.hide();
            loadMembers();
            showToast(`Пользователь ${username} добавлен!`, 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось добавить пользователя'), 'error');
        }
    } catch (error) {
        console.error('Ошибка добавления:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

async function removeMember(userId) {
    try {
        const response = await fetchWithAuth(`/api/projects/${projectId}/members/${userId}`, { method: 'DELETE' });
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmRemoveMemberModal'));
            if (modal) modal.hide();
            loadMembers();
            showToast('Участник удален!', 'success');
        } else {
            const error = await response.json();
            showToast('Ошибка: ' + (error.detail || 'Не удалось удалить пользователя'), 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showToast('Ошибка соединения с сервером', 'error');
    }
}

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