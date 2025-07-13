import PageWrapper from '@/components/PageWrapper';
import PricingCards from '@/components/PricingCards';
import PricingTable from '@/components/PricingTable';

export default function PricingPage() {
  return (
    <PageWrapper>
      <div className="space-y-12">
        <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
                Pricing Plans
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-gray-300">
                Choose the plan that's right for you. No hidden fees.
            </p>
        </div>

        {/* Pricing Cards Section */}
        <section>
            <PricingCards />
        </section>

        {/* Detailed Feature Comparison Table */}
        <section className="py-12">
            <div className="text-center mb-10">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Compare Plan Features
                </h2>
                <p className="mt-4 text-md text-gray-500 dark:text-gray-400">
                    A detailed look at what each plan offers.
                </p>
            </div>
            <PricingTable />
        </section>
      </div>
    </PageWrapper>
  );
}
