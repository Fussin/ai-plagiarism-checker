import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import HeaderNav from "@/components/HeaderNav"; // Import the new HeaderNav component

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Plagiarism Checker",
  description: "Check your content for plagiarism with AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col transition-colors duration-300`}>
        <Providers>
          <header className="bg-blue-600 dark:bg-gray-800 text-white p-4 shadow-md sticky top-0 z-50">
            <HeaderNav /> {/* Use the HeaderNav component here */}
          </header>
          <main className="flex-grow container mx-auto p-4">
            {children}
          </main>
          <footer className="bg-gray-700 dark:bg-gray-950 text-gray-300 dark:text-gray-400 text-center p-4 mt-auto">
            <p>&copy; {new Date().getFullYear()} AI Plagiarism Checker. All rights reserved.</p>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
