document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен!');

    const loginButton = document.getElementById('loginButton');
    const loginError = document.getElementById('loginError');

    if (!loginButton) {
        console.error('Кнопка не найдена!');
        return;
    }

    loginButton.addEventListener('click', async function() {
        console.log('Кнопка нажата!');

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !password) {
            loginError.textContent = 'Заполните все поля!';
            loginError.classList.remove('d-none');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                const userResponse = await fetch('/api/auth/me', {
                    headers: { 'Authorization': `Bearer ${data.access_token}` }
                });
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    localStorage.setItem('user_id', userData.id);
                    localStorage.setItem('username', userData.username); 
                }
                
                window.location.href = '/projects';
            } else {
                // 👇 ОБРАБОТКА ОШИБОК
                const errorData = await response.json();
                const errorMessage = errorData.detail || 'Неверное имя пользователя или пароль';
                loginError.textContent = errorMessage;
                loginError.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Ошибка запроса:', error);
            loginError.textContent = 'Ошибка соединения с сервером';
            loginError.classList.remove('d-none');
        }
    });
});