"use client";

import { motion, AnimatePresence } from 'framer-motion';
import { ReactNode } from 'react';

interface PageWrapperProps {
  children: ReactNode;
  className?: string; // Optional className for custom styling of the wrapper itself
}

export default function PageWrapper({ children, className }: PageWrapperProps) {
  return (
    // AnimatePresence can be useful if the children themselves might enter/exit,
    // but for a simple page load animation, motion.div is often enough.
    // If PageWrapper wraps content that is conditionally rendered *inside* a page,
    // then AnimatePresence might be more relevant at that inner level.
    // For now, a direct motion.div for the page content itself.
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }} // exit animation might not always be visible with App Router
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className={className} // Apply any custom classes passed to the wrapper
    >
      {children}
    </motion.div>
  );
}
