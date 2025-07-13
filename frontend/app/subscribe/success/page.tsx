"use client";

import { useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import PageWrapper from '@/components/PageWrapper';
import { CheckCircleIcon } from '@heroicons/react/24/solid';
import { useSearchParams } from 'next/navigation';

export default function SubscriptionSuccessPage() {
  const { fetchUser } = useAuth();
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // When the user lands here after a successful checkout, their plan might not have been
    // updated yet by the webhook. Fetching the user data again helps sync the client state
    // once the webhook has been processed.
    // A small delay can sometimes help ensure the webhook has had time to be processed.
    if (sessionId) {
        console.log("Subscription success, session_id:", sessionId);
        const timer = setTimeout(() => {
            fetchUser();
        }, 2000); // 2-second delay to allow webhook processing

        return () => clearTimeout(timer);
    }
  }, [sessionId, fetchUser]);

  return (
    <PageWrapper>
      <div className="flex flex-col items-center justify-center text-center py-20">
        <CheckCircleIcon className="w-24 h-24 text-green-500 mb-6" />
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Subscription Successful!
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Thank you for subscribing. Your plan has been upgraded. It may take a moment for all changes to apply.
        </p>
        <Link href="/history" className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-md shadow-sm hover:bg-indigo-700">
          Go to Your Dashboard
        </Link>
      </div>
    </PageWrapper>
  );
}
