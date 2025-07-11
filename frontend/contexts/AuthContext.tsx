"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation'; // Using App Router's navigation

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
  login: (emailOrFormData: string | FormData, password?: string) => Promise<boolean>;
  signup: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  fetchUser: () => Promise<void>; // Manually trigger user fetch
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Start true to check initial auth status
  const router = useRouter();

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
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      setUser(null); // Clear user on error
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (emailOrFormData: string | FormData, password?: string): Promise<boolean> => {
    setIsLoading(true);
    let body: URLSearchParams | string;
    let headers: HeadersInit = {};

    if (emailOrFormData instanceof FormData) { // For direct form data submission (not used in this example)
        body = new URLSearchParams(emailOrFormData as any);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    } else { // For email/password string pair
        const formData = new URLSearchParams();
        formData.append('username', emailOrFormData as string);
        formData.append('password', password!);
        body = formData.toString();
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: headers,
        body: body,
      });
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('authToken', data.access_token);
        await fetchUser(); // Fetch user details after successful login
        setIsLoading(false);
        return true;
      } else {
        console.error('Login failed:', data.detail);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const signup = async (email: string, password: string): Promise<boolean> => {
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
        await fetchUser(); // Fetch user details after successful signup
        setIsLoading(false);
        return true;
      } else {
        console.error('Signup failed:', data.detail);
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Signup error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
    router.push('/login'); // Redirect to login page on logout
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
