"use client";

import { planFeatures } from '@/lib/plans';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/solid';

export default function PricingTable() {
    const plans = ['free', 'pro_basic', 'pro_advanced', 'enterprise'];
    const planNames = ['Free Basic', 'Pro Basic', 'Pro Advanced', 'Enterprise'];

    return (
        <div className="w-full overflow-x-auto rounded-lg shadow-lg">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Features
                        </th>
                        {planNames.map(name => (
                            <th key={name} scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                {name}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {planFeatures.map((feature, featureIdx) => (
                        <tr key={feature.name} className={featureIdx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800/50'}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                                {feature.name}
                            </td>
                            {plans.map(planKey => {
                                const value = feature[planKey as keyof typeof feature];
                                return (
                                    <td key={`${feature.name}-${planKey}`} className="px-6 py-4 whitespace-pre-wrap text-center text-sm text-gray-500 dark:text-gray-300">
                                        {typeof value === 'boolean' ? (
                                            value ? <CheckIcon className="h-6 w-6 text-green-500 mx-auto" /> : <XMarkIcon className="h-6 w-6 text-red-500 mx-auto" />
                                        ) : (
                                            <span>{value}</span>
                                        )}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
