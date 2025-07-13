"use client";

import { useEffect, useState, useMemo } from 'react'; // Added useMemo
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import PageWrapper from '@/components/PageWrapper';
import { Squares2X2Icon, QueueListIcon } from '@heroicons/react/24/outline';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

interface ScanHistoryItem {
  id: number;
  content_type: string;
  file_name?: string;
  input_snippet?: string;
  originality_score: number;
  matched_sources: string[];
  rewrite_suggestions: string[];
  timestamp: string;
}

const ScanDetailModal = ({ item, onClose }: { item: ScanHistoryItem, onClose: () => void }) => {
  // ... (Modal component remains the same)
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0, y: -10 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.95, opacity: 0, y: 10 }}
        transition={{ duration: 0.2, ease: "easeOut" }}
        className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-blue-600 dark:text-blue-400">
                Scan Details: {item.file_name || item.content_type.replace(/_/g, " ")}
            </h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">&times;</button>
        </div>
        <p><strong>Date:</strong> {new Date(item.timestamp).toLocaleString()}</p>
        <p><strong>Type:</strong> {item.content_type}</p>
        {item.file_name && <p><strong>File:</strong> {item.file_name}</p>}
        {item.input_snippet && <p><strong>Snippet:</strong> <span className="italic">{item.input_snippet}</span></p>}
        <p><strong>Originality Score:</strong> <span className={`font-bold ${
            item.originality_score > 0.9 ? 'text-green-600 dark:text-green-400' :
            item.originality_score > 0.7 ? 'text-yellow-600 dark:text-yellow-400' :
                                        'text-red-600 dark:text-red-400'
        }`}>{(item.originality_score * 100).toFixed(1)}%</span></p>

        {item.matched_sources.length > 0 && (
          <div className="mt-3">
            <h4 className="font-semibold">Details & Matched Sources:</h4>
            <ul className="list-disc list-inside text-sm max-h-40 overflow-y-auto bg-gray-50 dark:bg-gray-700 p-2 rounded">
              {item.matched_sources.map((source, index) => <li key={index}>{source}</li>)}
            </ul>
          </div>
        )}
        {item.rewrite_suggestions.length > 0 && (
           <div className="mt-3">
            <h4 className="font-semibold">Rewrite Suggestions:</h4>
            <ul className="list-disc list-inside text-sm max-h-40 overflow-y-auto bg-gray-50 dark:bg-gray-700 p-2 rounded">
              {item.rewrite_suggestions.map((suggestion, index) => <li key={index}>{suggestion}</li>)}
            </ul>
          </div>
        )}
         <button onClick={onClose} className="mt-6 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white font-semibold rounded-md shadow-sm">
            Close
        </button>
      </motion.div>
    </motion.div>
  );
};

const filterOptions = ["all", "text", "file", "image", "video"];

export default function HistoryPage() {
  const { user, token, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [history, setHistory] = useState<ScanHistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedScan, setSelectedScan] = useState<ScanHistoryItem | null>(null);
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card');
  const [activeFilter, setActiveFilter] = useState('all'); // State for filtering

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace('/login?message=Please login to view history');
    } else if (user && token) {
      const fetchHistory = async () => {
        setIsLoadingHistory(true); setError(null);
        try {
          const response = await fetch(`${API_BASE_URL}/history/`, { headers: { 'Authorization': `Bearer ${token}` } });
          if (response.ok) {
            setHistory(await response.json());
          } else {
            const errorData = await response.json();
            setError(errorData.detail || "Failed to fetch history.");
          }
        } catch (err) { setError("An error occurred while fetching history.");
        } finally { setIsLoadingHistory(false); }
      };
      fetchHistory();
    }
  }, [user, token, authLoading, router]);

  const filteredHistory = useMemo(() => {
    if (activeFilter === 'all') {
      return history;
    }
    return history.filter(item => item.content_type.includes(activeFilter));
  }, [history, activeFilter]);

  if (authLoading || isLoadingHistory) {
    return <div className="text-center p-10">Loading history...</div>;
  }
  if (error) {
    return <div className="text-center p-10 text-red-500">Error: {error}</div>;
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i:number) => ({
      opacity: 1, y: 0, transition: { delay: i * 0.05, duration: 0.3 }
    })
  };

  const layoutTransition = {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 }
  }

  return (
    <PageWrapper className="space-y-8">
      <div className="flex flex-wrap gap-4 justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Scan History</h1>
        <div className="flex items-center space-x-4">
            {/* Filter Dropdown */}
            <div className="relative">
                 <select
                    value={activeFilter}
                    onChange={(e) => setActiveFilter(e.target.value)}
                    className="appearance-none w-full md:w-auto bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 py-2 pl-3 pr-8 rounded-lg leading-tight focus:outline-none focus:bg-white dark:focus:bg-gray-600 focus:border-gray-500"
                 >
                    {filterOptions.map(opt => (
                        <option key={opt} value={opt} className="capitalize">{opt.charAt(0).toUpperCase() + opt.slice(1)}</option>
                    ))}
                 </select>
                 <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-200">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
            </div>
            {/* View Toggle */}
            <div className="flex items-center space-x-1 p-1 bg-gray-200 dark:bg-gray-700 rounded-lg">
                <button onClick={() => setViewMode('card')} className={`p-1.5 rounded-md ${viewMode === 'card' ? 'bg-white dark:bg-gray-900 shadow' : 'hover:bg-gray-300 dark:hover:bg-gray-600'}`}>
                    <Squares2X2Icon className="h-5 w-5 text-gray-700 dark:text-gray-200" />
                </button>
                <button onClick={() => setViewMode('table')} className={`p-1.5 rounded-md ${viewMode === 'table' ? 'bg-white dark:bg-gray-900 shadow' : 'hover:bg-gray-300 dark:hover:bg-gray-600'}`}>
                    <QueueListIcon className="h-5 w-5 text-gray-700 dark:text-gray-200" />
                </button>
            </div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {filteredHistory.length === 0 ? (
          <motion.p {...layoutTransition} key="no-history" className="text-center text-gray-500 dark:text-gray-400 py-10">
            No scans found for the selected filter.
          </motion.p>
        ) : viewMode === 'card' ? (
          <motion.div {...layoutTransition} key="card-view" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredHistory.map((item, index) => (
              <motion.div key={item.id} className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 hover:shadow-xl transition-shadow duration-300 flex flex-col justify-between" variants={cardVariants} initial="hidden" animate="visible" custom={index} layout>
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <h2 className="text-xl font-semibold text-blue-600 dark:text-blue-400 capitalize">{item.file_name || item.content_type.replace(/_/g, " ")}</h2>
                    <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                      item.originality_score > 0.9 ? 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-200' :
                      item.originality_score > 0.7 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-200' : 'bg-red-100 text-red-800 dark:bg-red-700 dark:text-red-200'
                    }`}>{(item.originality_score * 100).toFixed(1)}%</span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{new Date(item.timestamp).toLocaleString()}</p>
                  {item.input_snippet && <p className="text-sm text-gray-700 dark:text-gray-300 truncate mb-4" title={item.input_snippet}>Snippet: {item.input_snippet}</p>}
                </div>
                <button onClick={() => setSelectedScan(item)} className="w-full mt-4 text-sm px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-md transition duration-150">View Details</button>
              </motion.div>
            ))}
          </motion.div>
        ) : (
           <motion.div {...layoutTransition} key="table-view" className="overflow-x-auto bg-white dark:bg-gray-800 shadow rounded-lg">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Content</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Score (%)</th>
                  <th scope="col" className="relative px-6 py-3"><span className="sr-only">Details</span></th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredHistory.map((item) => (
                  <motion.tr key={item.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white capitalize">{item.file_name || item.content_type.replace(/_/g, " ")}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{new Date(item.timestamp).toLocaleDateString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          item.originality_score > 0.9 ? 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-200' :
                          item.originality_score > 0.7 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-200' : 'bg-red-100 text-red-800 dark:bg-red-700 dark:text-red-200'
                        }`}>{(item.originality_score * 100).toFixed(1)}%</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => setSelectedScan(item)} className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-200">Details</button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {selectedScan && <ScanDetailModal item={selectedScan} onClose={() => setSelectedScan(null)} />}
      </AnimatePresence>
    </PageWrapper>
  );
}
