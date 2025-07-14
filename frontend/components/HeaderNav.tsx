"use client";

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import ThemeToggleButton from './ThemeToggleButton';

// Helper to format large numbers into k/M
const formatUsage = (num: number) => {
    if (num < 1000) return num;
    if (num < 1000000) return `${(num / 1000).toFixed(1)}k`;
    return `${(num / 1000000).toFixed(1)}M`;
}

export default function HeaderNav() {
  const { user, logout, isLoading, usageSummary } = useAuth();

  return (
    <nav className="container mx-auto flex justify-between items-center">
      <Link href="/" className="text-xl font-bold">
        AI Plag Checker
      </Link>
      <div className="flex items-center space-x-4">
        <Link href="/" className="hover:text-blue-200 dark:hover:text-blue-300">Home</Link>
        <Link href="/pricing" className="hover:text-blue-200 dark:hover:text-blue-300">Pricing</Link>
        {isLoading ? (
          <div className="h-5 w-20 bg-gray-500 dark:bg-gray-700 animate-pulse rounded-md"></div> // Placeholder for loading state
        ) : user ? (
          <>
            <Link href="/history" className="hover:text-blue-200 dark:hover:text-blue-300">History</Link>
            <div className="text-sm hidden sm:flex items-center space-x-2 bg-black/10 dark:bg-white/10 px-3 py-1 rounded-full">
              <span>{user.email}</span>
              {usageSummary && usageSummary.word_limit !== -1 && (
                <span className="text-xs font-mono bg-gray-500/50 px-2 py-0.5 rounded-full">
                    {formatUsage(usageSummary.words_scanned)} / {formatUsage(usageSummary.word_limit)} words
                </span>
              )}
            </div>
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
