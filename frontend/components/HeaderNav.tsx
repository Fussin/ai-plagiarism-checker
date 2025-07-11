"use client";

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ThemeToggleButton from './ThemeToggleButton';

export default function HeaderNav() {
  const { user, logout, isLoading } = useAuth();

  return (
    <nav className="container mx-auto flex justify-between items-center">
      <Link href="/" className="text-xl font-bold">
        AI Plag Checker
      </Link>
      <div className="flex items-center space-x-4">
        <Link href="/" className="hover:text-blue-200 dark:hover:text-blue-300">Home</Link>
        {isLoading ? (
          <div className="h-5 w-20 bg-gray-500 dark:bg-gray-700 animate-pulse rounded-md"></div> // Placeholder for loading state
        ) : user ? (
          <>
            <Link href="/history" className="hover:text-blue-200 dark:hover:text-blue-300">History</Link>
            <span className="text-sm hidden sm:inline">Welcome, {user.email}!</span>
            <button
              onClick={logout}
              className="px-3 py-1.5 text-sm bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 rounded-md shadow transition-colors"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="hover:text-blue-200 dark:hover:text-blue-300">Login</Link>
            <Link href="/register" className="hover:text-blue-200 dark:hover:text-blue-300">Register</Link>
          </>
        )}
        <ThemeToggleButton />
      </div>
    </nav>
  );
}
