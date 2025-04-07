const AuthService = {
    async login(email, password) {
        try {
            const response = await fetch('/api/auth/users/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                throw new Error('Грешка при вход');
            }

            const data = await response.json();
            localStorage.setItem('authToken', data.token);
            return data;
        } catch (error) {
            console.error('Грешка при вход:', error);
            throw error;
        }
    },

    async logout() {
        const token = localStorage.getItem('authToken');
        try {
            await fetch('/api/auth/users/logout/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`
                }
            });
            localStorage.removeItem('authToken');
        } catch (error) {
            console.error('Грешка при изход:', error);
            throw error;
        }
    },

    async verifyToken() {
        const token = localStorage.getItem('authToken');
        if (!token) return false;

        try {
            const response = await fetch('/api/auth/verify-token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token })
            });

            const data = await response.json();
            return data.valid;
        } catch {
            return false;
        }
    },

    getAuthHeader() {
        const token = localStorage.getItem('authToken');
        return token ? { 'Authorization': `Token ${token}` } : {};
    }
};

// Пример за използване:
async function makeAuthenticatedRequest(url, options = {}) {
    const headers = {
        ...options.headers,
        ...AuthService.getAuthHeader()
    };

    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        // Токенът е невалиден
        localStorage.removeItem('authToken');
        window.location.href = '/login';
    }
    return response;
}
