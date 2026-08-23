// static/js/api.js

const API_BASE = '/api';

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('access_token');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, {
        ...options,
        headers
    });

    // Если токен истек (401) — пробуем обновить
    if (response.status === 401) {
        console.warn('🔄 Токен истек, пробуем обновить...');

        const refreshed = await refreshToken();
        if (refreshed) {
            // Повторяем запрос с новым токеном
            const newToken = localStorage.getItem('access_token');
            headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, {
                ...options,
                headers
            });
        } else {
            // Если не удалось обновить — выходим
            console.warn('🚫 Не удалось обновить токен, выходим...');
            logout();
        }
    }

    return response;
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
        console.warn('❌ Нет refresh токена');
        return false;
    }

    try {
        console.log('📤 Отправляем refresh запрос...');
        const response = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            if (data.refresh_token) {
                localStorage.setItem('refresh_token', data.refresh_token);
            }
            console.log('✅ Токен обновлен!');
            return true;
        } else {
            console.warn('❌ Сервер вернул ошибку при обновлении токена:', response.status);
            // 👇 Принудительно удаляем refresh_token, чтобы выйти
            localStorage.removeItem('refresh_token');
            return false;
        }
    } catch (error) {
        console.error('❌ Ошибка при обновлении токена:', error);
        localStorage.removeItem('refresh_token');
        return false;
    }
}

function logout() {
    console.warn('🚪 Выход из системы...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    window.location.href = '/';
}