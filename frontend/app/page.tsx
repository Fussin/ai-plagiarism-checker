"use client";

import { useState, FormEvent, ChangeEvent } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Spinner from '@/components/Spinner';
import PageWrapper from '@/components/PageWrapper';
import { motion, AnimatePresence } from 'framer-motion';

interface ScanResult {
  originality_score: number;
  matched_sources: string[];
  rewrite_suggestions: string[];
}

interface HumanizerResult {
    original_text: string;
    humanized_text: string | null;
    model_used: string;
    error?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export default function HomePage() {
  const { user, token } = useAuth();

  const [textInput, setTextInput] = useState('');
  const [files, setFiles] = useState<{ [key: string]: File | null }>({
    textFile: null, imageFile: null, videoFile: null,
  });
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [currentScanType, setCurrentScanType] = useState<string | null>(null); // Used for display and button states

  const [humanizerInput, setHumanizerInput] = useState('');
  const [humanizerResult, setHumanizerResult] = useState<HumanizerResult | null>(null);
  const [isHumanizing, setIsHumanizing] = useState(false);
  const [humanizerError, setHumanizerError] = useState<string | null>(null);

  const [fileSelectedFeedback, setFileSelectedFeedback] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>, fileTypeKey: string) => {
    if (event.target.files && event.target.files[0]) {
      setFiles(prev => ({ ...prev, [fileTypeKey]: event.target.files![0] }));
      setFileSelectedFeedback(fileTypeKey);
      setTimeout(() => setFileSelectedFeedback(null), 1500);
    } else {
      setFiles(prev => ({ ...prev, [fileTypeKey]: null }));
    }
  };

  const saveHistory = async (contentTypeForHistory: string, resultData: ScanResult, fileName?: string, inputSnippet?: string) => {
    if (!user || !token) return;
    const historyPayload = {
      content_type: contentTypeForHistory, // Use the specific type for history
      file_name: fileName,
      input_snippet: inputSnippet ? inputSnippet.substring(0, 250) : `Scan of ${contentTypeForHistory}`,
      originality_score: resultData.originality_score,
      matched_sources: resultData.matched_sources,
      rewrite_suggestions: resultData.rewrite_suggestions,
    };
    try {
      await fetch(`${API_BASE_URL}/history/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(historyPayload),
      });
    } catch (historyError) {
      console.error('Failed to save history:', historyError);
    }
  };

  const handleTextSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!textInput.trim()) { setScanError("Please enter some text to check."); return; }
    setCurrentScanType("Text Input"); // Set scan type for UI feedback
    setIsScanning(true); setScanError(null); setScanResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/check/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token && { 'Authorization': `Bearer ${token}` }) },
        body: JSON.stringify({ text: textInput }),
      });
      const data = await response.json();
      if (response.ok) {
        setScanResult(data);
        if (user) await saveHistory("text_input", data, undefined, textInput);
      } else { setScanError(data.detail || "Failed to check text."); }
    } catch (err) { setScanError("An error occurred while checking text."); console.error(err);
    } finally { setIsScanning(false); }
  };

  const handleFileSubmit = async (fileTypeKey: string, endpoint: string, historyContentType: string) => {
    const file = files[fileTypeKey];
    if (!file) { setScanError(`Please select a ${fileTypeKey.replace('File','')} file.`); return; }

    const scanTypeForDisplay = `${fileTypeKey.replace('File','')} File: ${file.name}`;
    setCurrentScanType(scanTypeForDisplay); // For UI feedback and button state
    setIsScanning(true); setScanError(null); setScanResult(null);

    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { ...(token && { 'Authorization': `Bearer ${token}` }) },
        body: formData,
      });
      const data = await response.json();
      if (response.ok) {
        setScanResult(data);
        // Use historyContentType for saving, which is more specific (e.g., "file_pdf")
        if (user) await saveHistory(historyContentType, data, file.name, `Content of ${file.name}`);
      } else { setScanError(data.detail || `Failed to check ${fileTypeKey.replace('File','')} file.`); }
    } catch (err) { setScanError(`An error occurred while checking ${fileTypeKey.replace('File','')} file.`); console.error(err);
    } finally { setIsScanning(false); }
  };

  const exportResults = () => {
    if (!scanResult) { alert("No results to export."); return; }
    let reportText = `AI Plagiarism Check Report\nScan Type: ${currentScanType || 'N/A'}\nOriginality Score: ${(scanResult.originality_score * 100).toFixed(1)}%\n\nDetails & Matched Sources:\n`;
    reportText += scanResult.matched_sources.length > 0 ? scanResult.matched_sources.map(s => `- ${s}\n`).join('') : `No specific matches found.\n`;
    reportText += `\nRewrite Suggestions:\n`;
    reportText += scanResult.rewrite_suggestions.length > 0 ? scanResult.rewrite_suggestions.map(s => `- ${s}\n`).join('') : `No specific rewrite suggestions.\n`;
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `plagiarism_report_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link); link.click(); document.body.removeChild(link); URL.revokeObjectURL(link.href);
  };

  const handleHumanizeSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!humanizerInput.trim()) { setHumanizerError("Please enter some text to humanize."); return; }
    setIsHumanizing(true); setHumanizerError(null); setHumanizerResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/ai/humanize-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token && { 'Authorization': `Bearer ${token}` }) },
        body: JSON.stringify({ text: humanizerInput }),
      });
      const data: HumanizerResult = await response.json();
      if (response.ok && data.humanized_text) { setHumanizerResult(data); }
      else { setHumanizerError(data.error || "Failed to humanize text."); setHumanizerResult(data); }
    } catch (err) { setHumanizerError("An error occurred while humanizing text."); console.error(err);
    } finally { setIsHumanizing(false); }
  };

  const buttonBaseClass = "mt-2 px-4 py-1.5 text-white font-semibold rounded-md shadow-sm text-sm disabled:opacity-50 flex items-center justify-center min-w-[150px]";
  const greenButtonClass = `${buttonBaseClass} bg-green-500 hover:bg-green-600`;
  const purpleButtonClass = `${buttonBaseClass} bg-purple-500 hover:bg-purple-600`;

  const fileInputDivClass = (fileTypeKey: string) =>
    `p-4 border-2 border-dashed rounded-lg transition-colors duration-300 ease-in-out ${
      fileSelectedFeedback === fileTypeKey
        ? 'border-green-500 bg-green-50 dark:bg-green-900/30'
        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
    }`;

  return (
    <PageWrapper className="space-y-8">
      <section className="text-center py-12 bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-blue-700 dark:to-indigo-800 rounded-lg shadow-xl text-white">
        <h1 className="text-4xl font-bold mb-4">Advanced AI Plagiarism Checker</h1>
        <p className="text-lg mb-8 px-4">Upload your documents, text, images, or videos to check for originality.</p>
      </section>

      <form onSubmit={handleTextSubmit} className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Check Text Content</h2>
        <textarea value={textInput} onChange={(e) => setTextInput(e.target.value)} className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" rows={8} placeholder="Paste your text here to check for plagiarism..." disabled={isScanning}/>
        <button type="submit" disabled={isScanning} className={`${greenButtonClass} mt-4 px-6 py-2`}>
          {isScanning && currentScanType === "Text Input" ? <><Spinner size="w-5 h-5 mr-2" /> Checking...</> : 'Check Text'}
        </button>
      </form>

      <section className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Upload & Check Files</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className={fileInputDivClass('textFile')}>
            <label htmlFor="text-file-upload" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Text Document (PDF, DOCX, TXT)</label>
            <input type="file" id="text-file-upload" onChange={(e) => handleFileChange(e, 'textFile')} accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" className="w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-blue-900 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100 dark:hover:file:bg-blue-800 disabled:opacity-50" disabled={isScanning}/>
            <button onClick={() => handleFileSubmit('textFile', '/check/file', 'file_text')} disabled={isScanning || !files.textFile} className={`${greenButtonClass} w-full`}>
              {isScanning && currentScanType === `textFile File: ${files.textFile?.name}` ? <><Spinner size="w-4 h-4 mr-2" /> Checking...</> : 'Check Text File'}
            </button>
          </div>
          <div className={fileInputDivClass('imageFile')}>
            <label htmlFor="image-file-upload" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Image (JPG, PNG, GIF)</label>
            <input type="file" id="image-file-upload" onChange={(e) => handleFileChange(e, 'imageFile')} accept="image/jpeg,image/png,image/gif" className="w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-blue-900 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100 dark:hover:file:bg-blue-800 disabled:opacity-50" disabled={isScanning}/>
            <button onClick={() => handleFileSubmit('imageFile', '/check/image', 'file_image')} disabled={isScanning || !files.imageFile} className={`${greenButtonClass} w-full`}>
              {isScanning && currentScanType === `imageFile File: ${files.imageFile?.name}` ? <><Spinner size="w-4 h-4 mr-2" /> Checking...</> : 'Check Image File'}
            </button>
          </div>
          <div className={fileInputDivClass('videoFile')}>
            <label htmlFor="video-file-upload" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Video (MP4)</label>
            <input type="file" id="video-file-upload" onChange={(e) => handleFileChange(e, 'videoFile')} accept="video/mp4" className="w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 dark:file:bg-blue-900 file:text-blue-700 dark:file:text-blue-300 hover:file:bg-blue-100 dark:hover:file:bg-blue-800 disabled:opacity-50" disabled={isScanning}/>
            <button onClick={() => handleFileSubmit('videoFile', '/check/video', 'file_video')} disabled={isScanning || !files.videoFile} className={`${greenButtonClass} w-full`}>
             {isScanning && currentScanType === `videoFile File: ${files.videoFile?.name}` ? <><Spinner size="w-4 h-4 mr-2" /> Checking...</> : 'Check Video File'}
            </button>
          </div>
        </div>
      </section>

      <AnimatePresence>
        {(isScanning || scanResult || scanError) && (
          <motion.section
            id="results-preview-section"
            className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md"
            initial={{ opacity: 0, height: 0, y: 20 }}
            animate={{ opacity: 1, height: 'auto', y: 0 }}
            exit={{ opacity: 0, height: 0, y: 20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Scan Results {currentScanType ? `for ${currentScanType.replace(/_/g, " ").replace(/file /i, 'File: ')}` : ''}</h2>
            {isScanning && <div className="flex items-center text-indigo-600 dark:text-indigo-400"><Spinner size="w-5 h-5 mr-2" color="text-indigo-600 dark:text-indigo-400"/>Scanning, please wait...</div>}
            {scanError && <p className="text-red-500 dark:text-red-400">Error: {scanError}</p>}
            {scanResult && !isScanning && (
            <div className="space-y-3">
              <p><strong>Originality Score:</strong> <span className={`font-bold ${ scanResult.originality_score > 0.9 ? 'text-green-600 dark:text-green-400' : scanResult.originality_score > 0.7 ? 'text-yellow-600 dark:text-yellow-400' : 'text-red-600 dark:text-red-400' }`}>{(scanResult.originality_score * 100).toFixed(1)}%</span></p>
              {scanResult.matched_sources.length > 0 && ( <div> <h4 className="font-semibold mt-2">Details & Matched Sources:</h4> <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300 max-h-48 overflow-y-auto"> {scanResult.matched_sources.map((source, index) => <li key={index}>{source}</li>)} </ul> </div> )}
              {scanResult.rewrite_suggestions.length > 0 && ( <div> <h4 className="font-semibold mt-2">Rewrite Suggestions:</h4> <ul className="list-disc list-inside text-sm text-gray-700 dark:text-gray-300"> {scanResult.rewrite_suggestions.map((suggestion, index) => <li key={index}>{suggestion}</li>)} </ul> </div> )}
              <button onClick={exportResults} className="mt-4 px-6 py-2 bg-indigo-500 hover:bg-indigo-600 text-white font-semibold rounded-md shadow-sm transition duration-150"> Export Results </button>
            </div>
          )}
          </motion.section>
        )}
      </AnimatePresence>

      <form onSubmit={handleHumanizeSubmit} className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">GPT-Powered Text Humanizer</h2>
         <textarea value={humanizerInput} onChange={(e) => setHumanizerInput(e.target.value)} className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white" rows={5} placeholder="Paste text here to humanize..." disabled={isHumanizing}/>
        <button type="submit" disabled={isHumanizing} className={purpleButtonClass}>
          {isHumanizing ? <><Spinner size="w-5 h-5 mr-2" /> Humanizing...</> : 'Humanize Text'}
        </button>
        <AnimatePresence>
          {isHumanizing && !humanizerError && !humanizerResult && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-2 flex items-center text-purple-600 dark:text-purple-400">
              <Spinner size="w-5 h-5 mr-2" color="text-purple-600 dark:text-purple-400"/> Processing...
            </motion.div>
          )}
          {humanizerError && (
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-2 text-red-500 dark:text-red-400">Error: {humanizerError}</motion.p>
          )}
          {humanizerResult && !isHumanizing && (
              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y:10 }}
                className="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded-md min-h-[80px]"
              >
                  <h4 className="font-semibold text-gray-800 dark:text-white">Humanized Text (Model: {humanizerResult.model_used}):</h4>
                  {humanizerResult.humanized_text ? ( <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{humanizerResult.humanized_text}</p> ) : ( <p className="text-gray-500 dark:text-gray-400">Could not generate humanized text. {humanizerResult.error || ''}</p> )}
                  <div className="mt-2 pt-2 border-t dark:border-gray-700">
                      <h5 className="text-xs font-semibold text-gray-600 dark:text-gray-400">Original Text:</h5>
                      <p className="text-xs text-gray-500 dark:text-gray-500 whitespace-pre-wrap">{humanizerResult.original_text}</p>
                  </div>
              </motion.div>
          )}
          {!humanizerResult && !isHumanizing && !humanizerError && (
            <div className="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded-md min-h-[80px] text-gray-600 dark:text-gray-300">
              <p>Humanized text will appear here...</p>
            </div>
          )}
        </AnimatePresence>
      </form>
    </PageWrapper>
  );
}
