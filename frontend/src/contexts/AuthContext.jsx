import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { normalizeRole } from '../utils/auth';
import { AuthContext } from './auth-context';

const normalizeUser = (user) => ({
  ...user,
  role: normalizeRole(user.role),
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        
        const res = await apiClient.get('/api/v1/auth/me');
        const userData = normalizeUser(res.data);

        setUser(userData);
      } catch (err) {
        console.error("Auth restore failed:", err);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password
    });

    const { access_token } = response.data;

    localStorage.setItem('token', access_token);

    const profileRes = await apiClient.get('/api/v1/auth/me');

    const userData = normalizeUser(profileRes.data);

    setUser(userData);

    return userData;
  };

  const register = async (userData) => {
    const response = await apiClient.post('/api/v1/auth/register', userData);
    const { access_token } = response.data;

    localStorage.setItem('token', access_token);

    const profileRes = await apiClient.get('/api/v1/auth/me');
    const normalizedUser = normalizeUser(profileRes.data);

    setUser(normalizedUser);

    return normalizedUser;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
