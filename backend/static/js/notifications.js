// static/js/notifications.js

let currentPage = 1;
const limit = 10;
let totalPages = 1;
let currentFilter = 'all';
let selectedIds = new Set();
let allIds = [];
let pendingDeleteIds = [];

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    setUserName();
    loadNotifications();
    updateUnreadCount();

    // Выход
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

    // Выделить все
    document.getElementById('selectAllBtn').addEventListener('click', toggleSelectAll);

    // Фильтр
    document.getElementById('filterStatus').addEventListener('change', function() {
        currentFilter = this.value;
        currentPage = 1;
        selectedIds.clear();
        updateUI();
        loadNotifications();
    });

    document.getElementById('resetFilterBtn').addEventListener('click', function() {
        document.getElementById('filterStatus').value = 'all';
        currentFilter = 'all';
        currentPage = 1;
        selectedIds.clear();
        updateUI();
        loadNotifications();
    });

    // Массовые действия
    document.getElementById('bulkMarkReadBtn').addEventListener('click', bulkMarkAsRead);
    document.getElementById('bulkDeleteBtn').addEventListener('click', function() {
        if (selectedIds.size === 0) return;
        pendingDeleteIds = Array.from(selectedIds);
        document.getElementById('deleteCountText').textContent = `${pendingDeleteIds.length} уведомлений`;
        const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        modal.show();
    });

    // Подтверждение удаления в модалке
    document.getElementById('confirmDeleteBtn').addEventListener('click', async function() {
        if (pendingDeleteIds.length === 0) return;

        try {
            const response = await fetchWithAuth('/api/notifications/bulk-delete', {
                method: 'DELETE',
                body: JSON.stringify({ notification_ids: pendingDeleteIds })
            });

            if (response.ok) {
                const data = await response.json();
                showToast(`Удалено ${data.deleted_count} уведомлений`, 'success');
                pendingDeleteIds = [];
                selectedIds.clear();
                updateUI();
                await updateUnreadCount();
                loadNotifications(currentPage);
            } else {
                showToast('Ошибка при удалении', 'error');
            }
        } catch (error) {
            showToast('Ошибка соединения с сервером', 'error');
        }

        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteModal'));
        if (modal) modal.hide();
    });
});

// ========== ЗАГРУЗКА ==========

async function loadNotifications(page = 1) {
    const skip = (page - 1) * limit;
    currentPage = page;

    const container = document.getElementById('notificationsList');
    container.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
        </div>
    `;

    try {
        let url = `/api/notifications/?skip=${skip}&limit=${limit}`;
        if (currentFilter === 'unread') {
            url += '&is_read=false';
        } else if (currentFilter === 'read') {
            url += '&is_read=true';
        }

        const response = await fetchWithAuth(url);

        if (response.ok) {
            const data = await response.json();
            const notifications = data.items || [];
            const total = data.total || 0;
            allIds = notifications.map(n => n.id);
            totalPages = Math.ceil(total / limit) || 1;
            displayNotifications(notifications);
        } else {
            container.innerHTML = `<div class="alert alert-danger">Ошибка загрузки уведомлений</div>`;
        }
    } catch (error) {
        console.error('Ошибка:', error);
        container.innerHTML = `<div class="alert alert-danger">Ошибка соединения с сервером</div>`;
    }
}

// ========== ОТОБРАЖЕНИЕ ==========

function displayNotifications(notifications) {
    const container = document.getElementById('notificationsList');

    if (!notifications || notifications.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <p class="text-muted">У вас нет уведомлений</p>
            </div>
        `;
        document.getElementById('paginationContainer').innerHTML = '';
        return;
    }

    let html = '';
    notifications.forEach(notification => {
        const isRead = notification.is_read;
        const bgClass = isRead ? '' : 'list-group-item-warning';
        const icon = isRead ? '📩' : '🔔';
        const isChecked = selectedIds.has(notification.id) ? 'checked' : '';

        const date = new Date(notification.created_at);
        const formattedDate = date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        const link = notification.link
            ? `<a href="${notification.link}" class="btn btn-sm btn-outline-primary ms-2">Перейти</a>`
            : '';

        html += `
            <div class="list-group-item list-group-item-action ${bgClass} notification-item" data-id="${notification.id}">
                <div class="d-flex align-items-start gap-3">
                    <input type="checkbox" class="form-check-input mt-2 notification-checkbox" 
                           data-id="${notification.id}" ${isChecked}>
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center gap-2 flex-wrap">
                            <span>${icon}</span>
                            <strong>${notification.title || 'Уведомление'}</strong>
                            <span class="badge ${isRead ? 'bg-secondary' : 'bg-primary'}">
                                ${isRead ? 'Прочитано' : 'Новое'}
                            </span>
                            ${!isRead ? `
                                <button class="btn btn-sm btn-outline-success mark-read-btn" data-id="${notification.id}">
                                    ✓
                                </button>
                            ` : ''}
                        </div>
                        <p class="mb-1 mt-1">${notification.message}</p>
                        <small class="text-muted">${formattedDate}</small>
                    </div>
                    <div>
                        ${link}
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    document.querySelectorAll('.notification-checkbox').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = parseInt(this.dataset.id);
            if (this.checked) {
                selectedIds.add(id);
            } else {
                selectedIds.delete(id);
            }
            updateUI();
        });
    });

    document.querySelectorAll('.mark-read-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.stopPropagation();
            const notificationId = this.dataset.id;
            await markAsRead(notificationId);
        });
    });

    updateUI();
    renderPagination();
}

// ========== UI ==========

function updateUI() {
    const count = selectedIds.size;
    document.getElementById('selectedCount').textContent = `Выделено: ${count}`;

    const showButtons = count > 0;
    document.getElementById('bulkMarkReadBtn').style.display = showButtons ? 'inline-block' : 'none';
    document.getElementById('bulkDeleteBtn').style.display = showButtons ? 'inline-block' : 'none';

    const selectAllBtn = document.getElementById('selectAllBtn');
    const allSelected = allIds.length > 0 && allIds.every(id => selectedIds.has(id));
    selectAllBtn.textContent = allSelected ? '☑ Снять выделение' : '☑ Выделить все';
}

function toggleSelectAll() {
    const allSelected = allIds.length > 0 && allIds.every(id => selectedIds.has(id));

    if (allSelected) {
        selectedIds.clear();
    } else {
        allIds.forEach(id => selectedIds.add(id));
    }

    document.querySelectorAll('.notification-checkbox').forEach(cb => {
        const id = parseInt(cb.dataset.id);
        cb.checked = selectedIds.has(id);
    });

    updateUI();
}

// ========== ПАГИНАЦИЯ ==========

function renderPagination() {
    const container = document.getElementById('paginationContainer');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = `<nav><ul class="pagination">`;

    // Назад
    html += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage - 1})">←</button>
        </li>
    `;

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        html += `<li class="page-item"><button class="page-link" onclick="changePage(1)">1</button></li>`;
        if (startPage > 2) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <button class="page-link" onclick="changePage(${i})">${i}</button>
            </li>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        html += `<li class="page-item"><button class="page-link" onclick="changePage(${totalPages})">${totalPages}</button></li>`;
    }

    // Вперёд
    html += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage + 1})">→</button>
        </li>
    `;

    html += `</ul></nav>`;
    container.innerHTML = html;
}

function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    selectedIds.clear();
    updateUI();
    loadNotifications(page);
    window.scrollTo(0, 0);
}

// ========== МАССОВЫЕ ДЕЙСТВИЯ ==========

async function bulkMarkAsRead() {
    if (selectedIds.size === 0) return;

    try {
        const response = await fetchWithAuth('/api/notifications/bulk-read', {
            method: 'PUT',
            body: JSON.stringify({ notification_ids: Array.from(selectedIds) })
        });

        if (response.ok) {
            showToast(`Отмечено ${selectedIds.size} уведомлений`, 'success');
            selectedIds.clear();
            updateUI();
            await updateUnreadCount();
            loadNotifications(currentPage);
        } else {
            showToast('Ошибка при отметке', 'error');
        }
    } catch (error) {
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== ОТДЕЛЬНЫЕ ДЕЙСТВИЯ ==========

async function markAsRead(notificationId) {
    try {
        const response = await fetchWithAuth(`/api/notifications/${notificationId}/read`, {
            method: 'PUT'
        });

        if (response.ok) {
            showToast('Уведомление отмечено как прочитанное', 'success');
            await updateUnreadCount();
            loadNotifications(currentPage);
        } else {
            showToast('Ошибка при отметке', 'error');
        }
    } catch (error) {
        showToast('Ошибка соединения с сервером', 'error');
    }
}

// ========== ВСПОМОГАТЕЛЬНЫЕ ==========

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

function setUserName() {
    const username = localStorage.getItem('username');
    const userNameElement = document.getElementById('userName');
    if (username && userNameElement) {
        userNameElement.textContent = username;
    }
}