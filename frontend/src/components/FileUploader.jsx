import React, { useState } from 'react';
import './FileUploader.css';
import { FiUpload, FiFile, FiX, FiGithub, FiClipboard } from 'react-icons/fi';

function FileUploader({ onCodeLoaded }) {
  const [inputMethod, setInputMethod] = useState('upload');
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState('');
  const [code, setCode] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError('');

    const file = e.dataTransfer.files[0];
    if (file) {
      await processFile(file);
    }
  };

  const handleFileChange = async (e) => {
    e.preventDefault();
    setError('');
    const file = e.target.files[0];
    if (file) {
      await processFile(file);
    }
  };

  const processFile = async (file) => {
    const validExtensions = [
      '.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', 
      '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.tsx',
      '.jsx', '.html', '.css', '.json', '.xml'
    ];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError(`File type ${ext} not supported. Please upload a code file.`);
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10MB.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      setFileName(file.name);
      setCode(content);
      onCodeLoaded(content, file.name);
      setError('');
    };
    reader.onerror = () => {
      setError('Failed to read file. Please try again.');
    };
    reader.readAsText(file);
  };

  const handlePasteChange = (e) => {
    const pastedCode = e.target.value;
    setCode(pastedCode);
    setError('');
    
    // Detect file type from content
    const detectedType = detectLanguage(pastedCode);
    const filename = `pasted_code.${detectedType}`;
    
    setFileName(filename);
    onCodeLoaded(pastedCode, filename);
  };

  const detectLanguage = (code) => {
    if (code.includes('def ') && code.includes(':')) return 'py';
    if (code.includes('function ') || code.includes('=>')) return 'js';
    if (code.includes('public class')) return 'java';
    if (code.includes('#include')) return 'cpp';
    if (code.includes('<?php')) return 'php';
    if (code.includes('package main')) return 'go';
    return 'txt';
  };

  const handleGithubFetch = async () => {
    if (!githubUrl.trim()) {
      setError('Please enter a GitHub URL');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Convert various GitHub URL formats to raw URL
      let rawUrl = githubUrl.trim();
      
      // Handle github.com URLs
      if (rawUrl.includes('github.com')) {
        rawUrl = rawUrl
          .replace('github.com', 'raw.githubusercontent.com')
          .replace('/blob/', '/');
      }
      
      // Already raw URL - use as is
      if (rawUrl.includes('raw.githubusercontent.com')) {
        // URL is already in raw format
      }
      
      // Handle gist URLs
      if (rawUrl.includes('gist.github.com')) {
        setError('Please use the "Raw" button on the gist and paste that URL');
        setLoading(false);
        return;
      }

      console.log('Fetching from:', rawUrl);

      const response = await fetch(rawUrl);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
      }

      const content = await response.text();
      
      // Extract filename from URL
      const urlParts = githubUrl.split('/');
      const filename = urlParts[urlParts.length - 1] || 'github_code.py';

      setCode(content);
      setFileName(filename);
      onCodeLoaded(content, filename);
      setError('');
      
      console.log('✅ Successfully loaded from GitHub:', filename);
    } catch (error) {
      console.error('GitHub fetch error:', error);
      setError(`Failed to fetch from GitHub: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code).then(() => {
      alert('Code copied to clipboard!');
    }).catch(() => {
      setError('Failed to copy code');
    });
  };

  const handleClear = () => {
    setFileName('');
    setCode('');
    setGithubUrl('');
    setError('');
    onCodeLoaded('', '');
  };

  return (
    <div className="file-uploader">
      {/* Tab Selection */}
      <div className="input-method-tabs">
        <button
          className={`tab-btn ${inputMethod === 'upload' ? 'active' : ''}`}
          onClick={() => setInputMethod('upload')}
        >
          <FiUpload /> Upload File
        </button>
        <button
          className={`tab-btn ${inputMethod === 'paste' ? 'active' : ''}`}
          onClick={() => setInputMethod('paste')}
        >
          <FiClipboard /> Paste Code
        </button>
        <button
          className={`tab-btn ${inputMethod === 'github' ? 'active' : ''}`}
          onClick={() => setInputMethod('github')}
        >
          <FiGithub /> GitHub URL
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {!code ? (
        <>
          {/* UPLOAD TAB */}
          {inputMethod === 'upload' && (
            <div
              className={`dropzone ${dragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="file-input"
                onChange={handleFileChange}
                accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.html,.css,.json,.xml"
                style={{ display: 'none' }}
              />
              <label htmlFor="file-input" className="dropzone-label">
                <FiUpload className="upload-icon" />
                <h3>Drop your code file here</h3>
                <p>or click to browse</p>
                <span className="file-types">
                  Supports: Python, JavaScript, Java, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, HTML, CSS
                </span>
              </label>
            </div>
          )}

          {/* PASTE TAB */}
          {inputMethod === 'paste' && (
            <div className="paste-section">
              <textarea
                className="paste-textarea"
                placeholder="Paste your code here...

Example:
def hello():
    print('Hello, World!')
"
                rows={15}
                onChange={handlePasteChange}
                value={code}
              />
              <p className="paste-hint">
                💡 Just paste your code and it will be automatically analyzed
              </p>
            </div>
          )}

          {/* GITHUB TAB */}
          {inputMethod === 'github' && (
            <div className="github-section">
              <div className="github-input-group">
                <FiGithub className="github-icon" />
                <input
                  type="text"
                  className="github-input"
                  placeholder="https://github.com/username/repo/blob/main/file.py"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleGithubFetch();
                    }
                  }}
                />
                <button
                  className="github-fetch-btn"
                  onClick={handleGithubFetch}
                  disabled={loading}
                >
                  {loading ? '⏳ Fetching...' : '🔍 Fetch Code'}
                </button>
              </div>
              
              <div className="github-examples">
                <p className="github-hint">
                  <strong>📝 Supported URL formats:</strong>
                </p>
                <ul className="github-url-list">
                  <li>✅ https://github.com/user/repo/blob/main/file.py</li>
                  <li>✅ https://raw.githubusercontent.com/user/repo/main/file.py</li>
                  <li>✅ Click "Raw" button on any GitHub file and paste that URL</li>
                </ul>
                <p className="github-example">
                  <strong>💡 Quick Example:</strong> Try this URL:<br/>
                  <code>https://raw.githubusercontent.com/python/cpython/main/Lib/json/__init__.py</code>
                </p>
              </div>
            </div>
          )}
        </>
      ) : (
        /* Code Loaded - Show Editor */
        <div className="file-info">
          <div className="file-details">
            <FiFile className="file-icon" />
            <div className="file-name">{fileName}</div>
            <div className="file-stats">
              {code.split('\n').length} lines • {code.length} chars
            </div>
            <div className="file-actions">
              <button className="btn-copy" onClick={handleCopy} title="Copy code">
                📋 Copy
              </button>
              <button className="btn-clear" onClick={handleClear} title="Clear and start over">
                <FiX /> Clear
              </button>
            </div>
          </div>
          <textarea
            className="code-textarea"
            value={code}
            onChange={handlePasteChange}
            placeholder="Edit your code here..."
            rows={15}
            spellCheck={false}
          />
          <p className="edit-hint">
            💡 You can edit the code above before reviewing
          </p>
        </div>
      )}
    </div>
  );
}

export default FileUploader;