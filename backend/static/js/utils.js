// static/js/utils.js

// ========== ПЕРЕВОД СТАТУСОВ ==========
function translateStatus(status) {
    const translations = {
        // Для проектов
        'active': 'Активный',
        'archived': 'Архивный',
        // Для задач
        'pending': 'Ожидает',
        'in_progress': 'В работе',
        'done': 'Выполнено',
        'cancelled': 'Отменено',
        'overdue': 'Просрочено'
    };
    return translations[status] || status;
}

// ========== ПЕРЕВОД ПРИОРИТЕТОВ ==========
function translatePriority(priority) {
    const translations = {
        'low': 'Низкий',
        'medium': 'Средний',
        'high': 'Высокий',
        'critical': 'Критический'
    };
    return translations[priority] || priority;
}

// ========== ПОЛУЧИТЬ ЦВЕТ ДЛЯ СТАТУСА ==========
function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'archived': 'secondary',
        'pending': 'secondary',
        'in_progress': 'primary',
        'done': 'success',
        'cancelled': 'danger',
        'overdue': 'danger'
    };
    return colors[status] || 'secondary';
}

// ========== ПОЛУЧИТЬ ЦВЕТ ДЛЯ ПРИОРИТЕТА ==========
function getPriorityColor(priority) {
    const colors = {
        'low': 'info',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    };
    return colors[priority] || 'secondary';
}

// ========== ФОРМАТИРОВАНИЕ ДАТЫ ==========
function formatDate(dateString) {
    if (!dateString) return 'Без дедлайна';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function updateUnreadCount() {
    try {
        const response = await fetchWithAuth('/api/notifications/unread-count');
        if (response.ok) {
            const data = await response.json();
            const badge = document.getElementById('unreadBadge');
            if (badge) {
                const count = data.unread_count || 0;
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        }
    } catch (error) {
        console.error('Ошибка получения количества уведомлений:', error);
    }
}