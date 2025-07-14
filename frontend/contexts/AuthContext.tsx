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

interface UsageSummary {
    plan: string;
    words_scanned: number;
    word_limit: number;
    humanizer_uses: number;
    humanizer_limit: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  usageSummary: UsageSummary | null;
  login: (email: string, password?: string) => Promise<{ success: boolean; error?: string }>;
  signup: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  fetchUsage: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { addToast } = useToast();

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (token && !user) {
      fetchUser();
    } else if (!token) {
      setUser(null);
      setUsageSummary(null);
    }
  }, [token]);

  const fetchUsage = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${API_BASE_URL}/users/me/usage-summary`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        setUsageSummary(await response.json());
      } else {
        console.error("Failed to fetch usage summary.");
      }
    } catch (error) {
      console.error("Error fetching usage summary:", error);
    }
  };

  const fetchUser = async () => {
    if (!token) {
      setUser(null);
      setUsageSummary(null);
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
        await fetchUsage(); // Fetch usage after successfully fetching user
      } else {
        console.error('Failed to fetch user, token might be invalid');
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
        setUsageSummary(null);
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
    setUsageSummary(null); // Clear usage on logout
    localStorage.removeItem('authToken');
    addToast('You have been logged out.', 'info');
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, usageSummary, login, signup, logout, fetchUser, fetchUsage }}>
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
