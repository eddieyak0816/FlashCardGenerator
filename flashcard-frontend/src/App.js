

console.log("App component loaded");
import React, { useState } from 'react';

function App() {
  const [inputType, setInputType] = useState('url');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [exportFormat, setExportFormat] = useState('sheets');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    console.log('handleGenerate called');
    setLoading(true);
    setError(null);
    setResult(null);
    let content = inputType === 'url' ? url : text;
    try {
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_type: inputType,
          content,
          export_format: exportFormat,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || 'An error occurred.');
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Network error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-2">AI Flashcard Generator</h1>
        <p className="text-center text-gray-600 mb-8">Transform any content into engaging flashcards!</p>
        <div className="max-w-4xl mx-auto">
          {/* Main Input Card */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            {/* Input Type Selection */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Choose Your Input:</label>
              <div className="flex space-x-4">
                <button
                  type="button"
                  className={`flex-1 px-4 py-3 ${inputType === 'url' ? 'bg-blue-500' : 'bg-blue-200'} text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring transition duration-200`}
                  onClick={() => setInputType('url')}
                >
                  <span className="block text-lg mb-1">📺 YouTube URL</span>
                  <span className="text-sm text-blue-100">Generate from video content</span>
                </button>
                <button
                  type="button"
                  className={`flex-1 px-4 py-3 ${inputType === 'text' ? 'bg-green-500' : 'bg-green-200'} text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring transition duration-200`}
                  onClick={() => setInputType('text')}
                >
                  <span className="block text-lg mb-1">📝 Custom Text</span>
                  <span className="text-sm text-green-100">Paste your own content</span>
                </button>
              </div>
            </div>
            {/* URL Input */}
            {inputType === 'url' && (
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="url">YouTube URL:</label>
                <input
                  type="text"
                  id="url"
                  name="url"
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                />
              </div>
            )}
            {/* Text Input */}
            {inputType === 'text' && (
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="content">Your Content:</label>
                <textarea
                  id="content"
                  name="content"
                  rows={6}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-green-300"
                  placeholder="Paste your text content here..."
                  value={text}
                  onChange={e => setText(e.target.value)}
                />
              </div>
            )}
            {/* Export Options */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Export Format:</label>
              <select
                id="exportFormat"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring"
                value={exportFormat}
                onChange={e => setExportFormat(e.target.value)}
              >
                <option value="sheets">Google Sheets</option>
                <option value="anki">Anki CSV</option>
                <option value="both">Both Formats</option>
              </select>
            </div>
            {/* Generate Button */}
            <button
              className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring transition duration-200"
              onClick={() => { console.log('Button clicked'); handleGenerate(); }}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Flashcards'}
            </button>
            {/* Error Message */}
            {error && <div className="mt-4 text-red-600 text-center">{error}</div>}
            {/* Result Display */}
            {result && (
              <div className="mt-6">
                <h2 className="text-xl font-bold mb-2">Result</h2>
                {result.flashcards && Array.isArray(result.flashcards) && (
                  <ul className="list-disc pl-6">
                    {result.flashcards.slice(0, 10).map((card, idx) => (
                      <li key={idx}>{card.question} — {card.answer}</li>
                    ))}
                  </ul>
                )}
                {result.sheets_url && (
                  <div className="mt-2"><a href={result.sheets_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Open Google Sheet</a></div>
                )}
                {result.anki_file && (
                  <div className="mt-2"><a href={`/export?file=${result.anki_file}`} className="text-green-600 underline">Download Anki CSV</a></div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
