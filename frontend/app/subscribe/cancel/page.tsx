"use client";

import Link from 'next/link';
import PageWrapper from '@/components/PageWrapper';
import { XCircleIcon } from '@heroicons/react/24/solid';

export default function SubscriptionCancelPage() {
  return (
    <PageWrapper>
      <div className="flex flex-col items-center justify-center text-center py-20">
        <XCircleIcon className="w-24 h-24 text-red-500 mb-6" />
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Subscription Canceled
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Your subscription process was canceled. You have not been charged.
        </p>
        <div className="flex space-x-4">
            <Link href="/pricing" className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 font-semibold rounded-md shadow-sm hover:bg-gray-300 dark:hover:bg-gray-600">
                View Plans
            </Link>
            <Link href="/" className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-md shadow-sm hover:bg-indigo-700">
                Back to Home
            </Link>
        </div>
      </div>
    </PageWrapper>
  );
}
