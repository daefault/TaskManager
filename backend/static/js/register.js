// static/js/register.js
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const registerError = document.getElementById('registerError');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        clearErrors();

        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !email || !password) {
            registerError.textContent = 'Заполните все поля!';
            registerError.classList.remove('d-none');
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                
                // Получаем user_id
                const userResponse = await fetch('/api/auth/me', {
                    headers: { 'Authorization': `Bearer ${data.access_token}` }
                });
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    localStorage.setItem('user_id', userData.id);
                    localStorage.setItem('username', userData.username);
                }
                
                window.location.href = '/projects';
            } else if (response.status === 422) {
                // Ошибки валидации от Pydantic
                const errorData = await response.json();
                showFieldErrors(errorData);
            } else {
                // Другие ошибки (409, 400, 500 и т.д.)
                const errorData = await response.json();
                registerError.textContent = errorData.detail || 'Ошибка регистрации';
                registerError.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Ошибка запроса:', error);
            registerError.textContent = 'Ошибка соединения с сервером';
            registerError.classList.remove('d-none');
        }
    });
});

function clearErrors() {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    const registerError = document.getElementById('registerError');
    if (registerError) {
        registerError.classList.add('d-none');
        registerError.textContent = '';
    }
}

function showFieldErrors(errorData) {
    clearErrors();
    
    if (errorData.detail && Array.isArray(errorData.detail)) {
        errorData.detail.forEach(err => {
            const field = err.loc[err.loc.length - 1];
            const msg = err.msg;
            const fieldMap = {
                'username': 'username',
                'email': 'email',
                'password': 'password'
            };
            const inputId = fieldMap[field];
            if (inputId) {
                const inputElement = document.getElementById(inputId);
                const errorElement = document.getElementById(`${inputId}Error`);
                if (inputElement) {
                    inputElement.classList.add('is-invalid');
                }
                if (errorElement) {
                    errorElement.textContent = getUserFriendlyMessage(field, msg);
                }
            }
        });
    }
}

function getUserFriendlyMessage(field, msg) {
    const fieldNames = {
        'username': 'Имя пользователя',
        'email': 'Email',
        'password': 'Пароль'
    };
    const fieldName = fieldNames[field] || field;
    
    if (msg.includes('String should have at least')) {
        const min = msg.match(/\d+/)?.[0] || '3';
        return `Минимум ${min} символов`;
    }
    if (msg.includes('String should have at most')) {
        const max = msg.match(/\d+/)?.[0] || '50';
        return `Максимум ${max} символов`;
    }
    if (msg.includes('field required')) {
        return 'Поле обязательно для заполнения';
    }
    if (msg.includes('value_error.email')) {
        return 'Введите корректный email';
    }
    if (msg.includes('value_error')) {
        return 'Некорректное значение';
    }
    return msg;
}