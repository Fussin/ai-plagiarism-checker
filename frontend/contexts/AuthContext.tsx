"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from './ToastContext'; // Import useToast

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  // Add other user fields if needed by the frontend
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password?: string) => Promise<{ success: boolean; error?: string }>;
  signup: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { addToast } = useToast(); // Use the toast context

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
    }
    setIsLoading(false); // Done checking local storage
  }, []);

  useEffect(() => {
    if (token && !user) { // If token exists but no user data, fetch user
      fetchUser();
    } else if (!token) {
      setUser(null); // Clear user if no token
    }
  }, [token]); // Rerun when token changes

  const fetchUser = async () => {
    if (!token) {
      setUser(null);
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token might be invalid or expired
        console.error('Failed to fetch user, token might be invalid');
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        // Optionally redirect to login if on a protected page, handled by page components
        addToast('Session expired. Please log in again.', 'error');
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      setUser(null); // Clear user on error
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password?: string) => {
    setIsLoading(true);
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password!);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('authToken', data.access_token);
        await fetchUser();
        addToast('Login successful!', 'success');
        return { success: true };
      } else {
        const errorMsg = data.detail || "Login failed. Please check your credentials.";
        addToast(errorMsg, 'error');
        return { success: false, error: errorMsg };
      }
    } catch (error) {
      console.error('Login network error:', error);
      addToast('A network error occurred during login.', 'error');
      return { success: false, error: 'A network error occurred.' };
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('authToken', data.access_token);
        await fetchUser();
        addToast('Signup successful! You are now logged in.', 'success');
        return { success: true };
      } else {
        const errorMsg = data.detail || 'Signup failed. Please try again.';
        addToast(errorMsg, 'error');
        return { success: false, error: errorMsg };
      }
    } catch (error) {
      console.error('Signup network error:', error);
      addToast('A network error occurred during signup.', 'error');
      return { success: false, error: 'A network error occurred.' };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
    addToast('You have been logged out.', 'info');
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
