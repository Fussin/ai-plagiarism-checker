"use client";

import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon } from '@heroicons/react/24/solid';

export interface ToastMessage {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

interface ToastProps {
  toast: ToastMessage;
  onRemove: (id: number) => void;
}

export default function Toast({ toast, onRemove }: ToastProps) {
  const toastVariants = {
    initial: { opacity: 0, y: 50, scale: 0.3 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, scale: 0.5, transition: { duration: 0.2 } },
  };

  const typeClasses = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    info: 'bg-blue-500 text-white',
  };

  return (
    <motion.div
      layout
      variants={toastVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className={`relative flex items-center justify-between w-full max-w-sm p-4 my-2 rounded-lg shadow-lg ${typeClasses[toast.type]}`}
    >
      <div className="flex-1 pr-4">{toast.message}</div>
      <button
        onClick={() => onRemove(toast.id)}
        className="p-1 rounded-full hover:bg-black/20 focus:outline-none focus:ring-2 focus:ring-white"
      >
        <XMarkIcon className="w-5 h-5" />
      </button>
    </motion.div>
  );
}

// A container for all toasts
interface ToastContainerProps {
    toasts: ToastMessage[];
    onRemoveToast: (id: number) => void;
}
export const ToastContainer = ({toasts, onRemoveToast}: ToastContainerProps) => {
    return (
        <div className="fixed bottom-5 right-5 z-[100] flex flex-col items-end">
            <AnimatePresence>
                {toasts.map((toast) => (
                    <Toast key={toast.id} toast={toast} onRemove={onRemoveToast} />
                ))}
            </AnimatePresence>
        </div>
    )
}
