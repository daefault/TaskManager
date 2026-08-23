// static/js/projects.js

let currentPage = 1;
const limit = 12;
let currentSearchQuery = '';

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    setUserName();
    loadProjects();
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
    document.getElementById('createProjectBtn').addEventListener('click', function() {
        clearCreateErrors();
        document.getElementById('createProjectForm').reset();
        const modal = new bootstrap.Modal(document.getElementById('createProjectModal'));
        modal.show();
    });

    document.getElementById('createProjectForm').addEventListener('submit', createProject);

    // ===== ПОИСК =====
    document.getElementById('searchProjectsBtn').addEventListener('click', function() {
        const query = document.getElementById('searchProjectsInput').value.trim();
        currentSearchQuery = query;
        currentPage = 1;
        loadProjects();
        document.getElementById('clearSearchBtn').style.display = query ? 'inline-block' : 'none';
    });

    document.getElementById('searchProjectsInput').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('searchProjectsBtn').click();
        }
    });

    document.getElementById('clearSearchBtn').addEventListener('click', function() {
        document.getElementById('searchProjectsInput').value = '';
        currentSearchQuery = '';
        currentPage = 1;
        loadProjects();
        this.style.display = 'none';
    });

    // ===== ФИЛЬТРЫ =====
    document.getElementById('filterStatus').addEventListener('change', function() {
        currentPage = 1;
        loadProjects();
    });

    document.getElementById('resetFiltersBtn').addEventListener('click', function() {
        document.getElementById('filterStatus').value = '';
        document.getElementById('searchProjectsInput').value = '';
        currentSearchQuery = '';
        currentPage = 1;
        document.getElementById('clearSearchBtn').style.display = 'none';
        loadProjects();
    });
});

// ========== УСТАНОВКА ИМЕНИ ==========
function setUserName() {
    const username = localStorage.getItem('username');
    const userNameElement = document.getElementById('userName');
    if (username && userNameElement) {
        userNameElement.textContent = username;
    }
}

// ========== ЗАГРУЗКА ПРОЕКТОВ ==========
async function loadProjects() {
    const token = localStorage.getItem('access_token');
    const skip = (currentPage - 1) * limit;
    const status = document.getElementById('filterStatus').value;
    const query = document.getElementById('searchProjectsInput').value.trim();

    let url = `/api/projects/?skip=${skip}&limit=${limit}&_=${Date.now()}`;
    if (status) url += `&status=${status}`;
    if (query) url += `&q=${encodeURIComponent(query)}`;

    try {
        const response = await fetchWithAuth(url);

        if (response.status === 401) {
            const refreshed = await refreshToken();
            if (refreshed) {
                loadProjects();
                return;
            } else {
                window.location.href = '/';
                return;
            }
        }

        if (!response.ok) {
            throw new Error('Ошибка загрузки проектов');
        }

        const data = await response.json();
        displayProjects(data.items, data.total);
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('projectsList').innerHTML = `
            <div class="col-12 text-center py-5 text-danger">
                Не удалось загрузить проекты
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
    }
}

// ========== ОТОБРАЖЕНИЕ ПРОЕКТОВ ==========
function displayProjects(projects, total) {
    const container = document.getElementById('projectsList');

    if (projects.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <p class="text-muted">
                    ${currentSearchQuery ? 'Проекты не найдены' : 'У вас пока нет проектов. Создайте свой первый проект!'}
                </p>
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }

    let html = '';
    projects.forEach(project => {
        const currentUserId = parseInt(localStorage.getItem('user_id'));
        const isOwner = project.owner_id === currentUserId;
        html += `
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title text-truncate" style="max-width: 80%;" title="${project.name}">${project.name}</h5>
                            ${isOwner ? '<span class="badge bg-warning text-dark flex-shrink-0">👑 Владелец</span>' : ''}
                        </div>
                        <span class="badge bg-${getStatusColor(project.status)}">
                            ${translateStatus(project.status)}
                        </span>
                    </div>
                    <div class="card-footer bg-transparent">
                        <a href="/projects/${project.id}" class="btn btn-outline-primary btn-sm w-100">
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
    loadProjects();
    window.scrollTo(0, 0);
}

// ========== ОЧИСТКА ОШИБОК ==========
function clearCreateErrors() {
    document.querySelectorAll('#createProjectForm .is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('#createProjectForm .invalid-feedback').forEach(el => el.textContent = '');
}

function showCreateFieldErrors(errorData) {
    clearCreateErrors();
    
    if (errorData.detail && Array.isArray(errorData.detail)) {
        const errors = errorData.detail;
        errors.forEach(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            const fieldMap = {
                'name': 'projectName',
                'description': 'projectDescription'
            };
            const inputId = fieldMap[field];
            if (!inputId) return;
            const inputElement = document.getElementById(inputId);
            const errorElement = document.getElementById(`${field}Error`);
            if (inputElement) inputElement.classList.add('is-invalid');
            if (errorElement) {
                let userMessage = msg;
                if (msg.includes('String should have at least')) {
                    const min = msg.match(/\d+/)?.[0] || '3';
                    userMessage = `Минимум ${min} символов`;
                } else if (msg.includes('String should have at most')) {
                    const max = msg.match(/\d+/)?.[0] || '200';
                    userMessage = `Максимум ${max} символов`;
                } else if (msg.includes('field required')) {
                    userMessage = 'Поле обязательно для заполнения';
                }
                errorElement.textContent = userMessage;
            }
        });
    }
}

// ========== СОЗДАНИЕ ПРОЕКТА ==========
async function createProject(event) {
    event.preventDefault();
    const token = localStorage.getItem('access_token');
    clearCreateErrors();

    const name = document.getElementById('projectName').value.trim();
    const description = document.getElementById('projectDescription').value.trim();

    if (!name) {
        document.getElementById('projectName').classList.add('is-invalid');
        document.getElementById('nameError').textContent = 'Поле обязательно для заполнения';
        return;
    }
    if (description.length > 2000) {
        document.getElementById('projectDescription').classList.add('is-invalid');
        document.getElementById('descriptionError').textContent = 'Максимум 2000 символов';
        return;
    }

    try {
        const response = await fetchWithAuth('/api/projects/', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createProjectModal'));
            modal.hide();
            document.getElementById('projectName').value = '';
            document.getElementById('projectDescription').value = '';
            currentPage = 1;
            loadProjects();
            showToast('Проект создан!', 'success');
        } else if (response.status === 422) {
            const errorData = await response.json();
            showCreateFieldErrors(errorData);
        } else {
            const error = await response.json();
            if (error.detail && error.detail.includes('уже существует')) {
                document.getElementById('projectName').classList.add('is-invalid');
                document.getElementById('nameError').textContent = error.detail;
            } else {
                showToast('Ошибка: ' + (error.detail || 'Не удалось создать проект'), 'error');
            }
        }
    } catch (error) {
        console.error('Ошибка создания проекта:', error);
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