"use client";

import Link from 'next/link';
import { useState, FormEvent, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Spinner from '@/components/Spinner';
import PageWrapper from '@/components/PageWrapper';

// Validation utility
const validateEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // State for individual field errors
  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    form: '', // For general form errors on submit
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signup, isLoading: authIsLoading, user } = useAuth();
  const router = useRouter();

  const handleValidation = (field: 'email' | 'password' | 'confirmPassword') => {
    let errorMsg = '';
    switch (field) {
      case 'email':
        if (!email) errorMsg = "Email is required.";
        else if (!validateEmail(email)) errorMsg = "Please enter a valid email address.";
        break;
      case 'password':
        if (!password) errorMsg = "Password is required.";
        else if (password.length < 8) errorMsg = "Password must be at least 8 characters long.";
        break;
      case 'confirmPassword':
        if (!confirmPassword) errorMsg = "Please confirm your password.";
        else if (password && password !== confirmPassword) errorMsg = "Passwords do not match.";
        break;
    }
    setErrors(prev => ({ ...prev, [field]: errorMsg }));
    return !errorMsg;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Run all validations before submitting
    const isEmailValid = handleValidation('email');
    const isPasswordValid = handleValidation('password');
    const isConfirmPasswordValid = handleValidation('confirmPassword');

    if (!isEmailValid || !isPasswordValid || !isConfirmPasswordValid) {
      return;
    }

    setErrors(prev => ({ ...prev, form: '' }));
    setIsSubmitting(true);

    const result = await signup(email, password);

    if (result.success) {
      router.push('/');
    } else {
      setErrors(prev => ({ ...prev, form: result.error || 'Signup failed. The email might already be registered.' }));
    }
    setIsSubmitting(false);
  };

  useEffect(() => {
    if (!authIsLoading && user) {
      router.replace('/');
    }
  }, [user, authIsLoading, router]);

  if (authIsLoading || (!authIsLoading && user)) {
    return <div className="text-center p-10">Loading...</div>;
  }

  return (
    <PageWrapper>
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)]">
        <div className="w-full max-w-md p-8 space-y-6 bg-white dark:bg-gray-800 shadow-xl rounded-lg">
          <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white">Create Account</h1>
          {errors.form && <p className="text-red-500 text-sm text-center bg-red-100 dark:bg-red-900/30 p-2 rounded-md">{errors.form}</p>}
          <form className="space-y-4" onSubmit={handleSubmit} noValidate>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => handleValidation('email')}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white ${errors.email ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
              />
              {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email}</p>}
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={() => handleValidation('password')}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white ${errors.password ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
                placeholder="At least 8 characters"
              />
               {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password}</p>}
            </div>
            <div>
              <label
                htmlFor="confirm-password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Confirm Password
              </label>
              <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onBlur={() => handleValidation('confirmPassword')}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:text-white ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
              />
              {errors.confirmPassword && <p className="mt-1 text-xs text-red-500">{errors.confirmPassword}</p>}
            </div>
            <div className="pt-2">
              <button
                type="submit"
                disabled={isSubmitting || authIsLoading}
                className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-indigo-500 dark:hover:bg-indigo-600 disabled:opacity-50"
              >
                {isSubmitting || authIsLoading ? (<><Spinner size="w-4 h-4 mr-2" /> Registering...</>) : ('Register')}
              </button>
            </div>
          </form>
          <p className="text-sm text-center text-gray-600 dark:text-gray-400">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </PageWrapper>
  );
}
