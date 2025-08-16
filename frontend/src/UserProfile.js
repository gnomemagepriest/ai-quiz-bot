import React, { useEffect, useState } from 'react';
import axios from 'axios';
import jwt_decode from 'jwt-decode';

const UserProfile = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            setError('Вы не авторизованы');
            setLoading(false);
            return;
        }

        try {
            const decodedToken = jwt_decode(token);
            axios.get(`http://localhost:5000/api/user`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            .then(response => {
                setUser(response.data);
                setLoading(false);
            })
            .catch(err => {
                setError('Ошибка при загрузке данных пользователя');
                setLoading(false);
            });
        } catch (err) {
            setError('Недействительный токен');
            setLoading(false);
        }
    }, []);

    if (loading) return <p>Загрузка...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div>
            <h2>Профиль пользователя</h2>
            <p>Имя пользователя: {user.username}</p>
        </div>
    );
};

export default UserProfile;
