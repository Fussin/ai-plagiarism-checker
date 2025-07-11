"use client";

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/solid'; // Using Heroicons for icons

export default function ThemeToggleButton() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme, resolvedTheme } = useTheme();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Return a placeholder or null to avoid hydration mismatch
    return <div className="w-6 h-6" />; // Placeholder with same size as button
  }

  const toggleTheme = () => {
    // If theme is system, toggle based on resolvedTheme, otherwise toggle between light/dark
    if (theme === 'system') {
      setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
    } else {
      setTheme(theme === 'dark' ? 'light' : 'dark');
    }
  };

  // Determine which icon to show based on the currently resolved theme
  const currentTheme = theme === 'system' ? resolvedTheme : theme;

  return (
    <button
      aria-label="Toggle Dark Mode"
      type="button"
      className="p-2 rounded-full hover:bg-gray-700 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white"
      onClick={toggleTheme}
    >
      {currentTheme === 'dark' ? (
        <SunIcon className="h-5 w-5 text-yellow-400" />
      ) : (
        <MoonIcon className="h-5 w-5 text-blue-200" />
      )}
    </button>
  );
}
