"use client";

import { ThemeProvider } from 'next-themes';
import { AuthProvider } from '@/contexts/AuthContext'; // Import AuthProvider
import { useEffect, useState, ReactNode } from 'react';

export default function Providers({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // To prevent hydration mismatch, children are rendered directly on the server.
    // On the client, once mounted, the providers will wrap them.
    // This might cause a flicker if initial theme/auth state affects layout significantly before JS loads.
    // Alternatively, return a loading skeleton or null.
    return <>{children}</>;
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  );
}
