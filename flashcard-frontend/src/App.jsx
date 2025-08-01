
import React, { useState } from 'react';

const defaultPrompts = [
  {
    name: 'Default Prompt',
    text: 'Summarize the video and generate flashcards for key concepts.'
  },
  {
    name: 'Vocabulary Focus',
    text: 'Extract vocabulary words and definitions from the video.'
  }
];

function App() {
  const [prompts, setPrompts] = useState(defaultPrompts);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [editText, setEditText] = useState(prompts[0].text);
  const [editName, setEditName] = useState(prompts[0].name);

  // Handle dropdown change
  const handleSelect = (e) => {
    const idx = parseInt(e.target.value, 10);
    setSelectedIndex(idx);
    setEditText(prompts[idx].text);
    setEditName(prompts[idx].name);
  };

  // Save changes to current prompt
  const handleSave = () => {
    const updated = [...prompts];
    updated[selectedIndex] = { name: editName, text: editText };
    setPrompts(updated);
  };

  // Add new prompt
  const handleAdd = () => {
    setPrompts([...prompts, { name: editName, text: editText }]);
    setSelectedIndex(prompts.length);
  };

  // Delete current prompt
  const handleDelete = () => {
    if (prompts.length === 1) return;
    const updated = prompts.filter((_, i) => i !== selectedIndex);
    setPrompts(updated);
    setSelectedIndex(0);
    setEditText(updated[0].text);
    setEditName(updated[0].name);
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-2">AI Flashcard Generator</h1>
        <p className="text-center text-gray-600 mb-8">Transform any content into engaging flashcards!</p>
        <div className="max-w-4xl mx-auto">
          {/* Prompt Management Card */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Prompt Presets:</label>
              <select value={selectedIndex} onChange={handleSelect} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring mb-2">
                {prompts.map((p, i) => (
                  <option key={i} value={i}>{p.name}</option>
                ))}
              </select>
              <input
                type="text"
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring mb-2"
                value={editName}
                onChange={e => setEditName(e.target.value)}
                placeholder="Prompt Name"
              />
              <textarea
                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring mb-2"
                rows={3}
                value={editText}
                onChange={e => setEditText(e.target.value)}
                placeholder="Prompt Text"
              />
              <div className="flex space-x-2">
                <button onClick={handleSave} className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">Save</button>
                <button onClick={handleAdd} className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600">Add New</button>
                <button onClick={handleDelete} className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600" disabled={prompts.length === 1}>Delete</button>
              </div>
            </div>
            {/* ...existing input UI... */}
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Choose Your Input:</label>
              <div className="flex space-x-4">
                <button className="flex-1 px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring transition duration-200">
                  <span className="block text-lg mb-1">📺 YouTube URL</span>
                  <span className="text-sm text-blue-100">Generate from video content</span>
                </button>
                <button className="flex-1 px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring transition duration-200">
                  <span className="block text-lg mb-1">📝 Custom Text</span>
                  <span className="text-sm text-green-100">Paste your own content</span>
                </button>
              </div>
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="url">YouTube URL:</label>
              <input type="text" id="url" className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300" placeholder="https://www.youtube.com/watch?v=..." />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="content">Your Content:</label>
              <textarea id="content" rows={6} className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-green-300" placeholder="Paste your text content here..." />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">Export Format:</label>
              <select id="exportFormat" className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring">
                <option value="sheets">Google Sheets</option>
              </select>
            </div>
            <button className="w-full bg-purple-600 text-white py-3 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring transition duration-200">Generate Flashcards</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
