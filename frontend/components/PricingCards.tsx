"use client";

import { planCards } from '@/lib/plans';
import { CheckIcon } from '@heroicons/react/24/solid';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function PricingCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {planCards.map((card, index) => (
        <motion.div
          key={index}
          whileHover={{ y: -5, scale: 1.02 }}
          transition={{ duration: 0.2 }}
          className={`relative flex flex-col p-8 rounded-2xl shadow-lg border-2 ${
            card.is_most_popular
            ? 'border-indigo-500 bg-white dark:bg-gray-800'
            : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50'
          }`}
        >
          {card.is_most_popular && (
            <div className="absolute top-0 -translate-y-1/2 px-3 py-1 text-sm text-white bg-indigo-500 rounded-full shadow-md">
              Most Popular
            </div>
          )}

          <h3 className="text-2xl font-semibold text-gray-900 dark:text-white">{card.name}</h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">{card.description}</p>
          <div className="mt-6">
            <span className="text-4xl font-bold text-gray-900 dark:text-white">{card.price}</span>
            <span className="text-base font-medium text-gray-500 dark:text-gray-400">{card.price_detail}</span>
          </div>

          <ul role="list" className="mt-8 space-y-4 flex-grow">
            {card.features.map((feature, i) => (
              <li key={i} className="flex items-start">
                <div className="flex-shrink-0">
                  <CheckIcon className="h-6 w-6 text-green-500" aria-hidden="true" />
                </div>
                <p className="ml-3 text-base text-gray-700 dark:text-gray-300">{feature}</p>
              </li>
            ))}
          </ul>

          <Link
            href={card.cta_link}
            className={`mt-10 block w-full text-center px-6 py-3 text-base font-medium rounded-md shadow-sm ${
                card.is_most_popular
                ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                : 'bg-white dark:bg-gray-700 text-indigo-600 dark:text-indigo-300 border border-indigo-600 dark:border-indigo-400 hover:bg-indigo-50 dark:hover:bg-gray-600'
            }`}
          >
            {card.cta_text}
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
