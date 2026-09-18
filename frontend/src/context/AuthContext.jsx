import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(() => {
    const savedUserId = localStorage.getItem('user_id');
    const savedName = localStorage.getItem('user_name');
    const savedEmail = localStorage.getItem('user_email');
    return savedUserId ? { user_id: savedUserId, user_name: savedName, email: savedEmail } : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('token');
      if (savedToken) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          localStorage.setItem('user_id', profile.user_id);
          localStorage.setItem('user_name', profile.user_name);
          localStorage.setItem('user_email', profile.email);
        } catch (err) {
          // Token invalid or expired
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authApi.login({ email, password });
    localStorage.setItem('token', data.token);
    localStorage.setItem('user_id', data.user_id);
    setToken(data.token);

    // Fetch user details
    try {
      const profile = await authApi.getMe();
      setUser(profile);
      localStorage.setItem('user_name', profile.user_name);
      localStorage.setItem('user_email', profile.email);
    } catch (e) {
      setUser({ user_id: data.user_id, email });
    }
    return data;
  };

  const signup = async (userData) => {
    const data = await authApi.signup(userData);
    localStorage.setItem('token', data.token);
    localStorage.setItem('user_id', data.user_id);
    setToken(data.token);

    try {
      const profile = await authApi.getMe();
      setUser(profile);
      localStorage.setItem('user_name', profile.user_name);
      localStorage.setItem('user_email', profile.email);
    } catch (e) {
      setUser({ user_id: data.user_id, user_name: userData.user_name, email: userData.email });
    }
    return data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        token,
        user,
        loading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
