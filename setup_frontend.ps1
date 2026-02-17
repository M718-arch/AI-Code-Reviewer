# setup_frontend.ps1
Write-Host "🚀 Setting up React frontend..." -ForegroundColor Cyan

# Create component directories
New-Item -ItemType Directory -Path "frontend/src/components" -Force | Out-Null
New-Item -ItemType Directory -Path "frontend/src/services" -Force | Out-Null

# Create App.js
@"
import React, { useState } from 'react';
import './App.css';
import FileUploader from './components/FileUploader';
import CodePreview from './components/CodePreview';
import IssueList from './components/IssueList';
import Metrics from './components/Metrics';
import { reviewCode } from './services/api';
import { Toaster, toast } from 'react-hot-toast';

function App() {
  const [code, setCode] = useState('');
  const [filename, setFilename] = useState('');
  const [language, setLanguage] = useState('');
  const [issues, setIssues] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCodeLoaded = (loadedCode, loadedFilename) => {
    setCode(loadedCode);
    setFilename(loadedFilename);
    setIssues([]);
    setSummary(null);
    setStats(null);
    toast.success(`✅ Loaded: ${loadedFilename}`);
  };

  const handleReview = async () => {
    if (!code.trim()) {
      toast.error('Please enter code first');
      return;
    }

    setLoading(true);
    try {
      const result = await reviewCode(code, filename);
      setIssues(result.issues);
      setSummary(result.summary);
      setStats(result.stats);
      setLanguage(result.language);
      toast.success(`✅ Found ${result.issues.length} issues`);
    } catch (error) {
      toast.error('Error analyzing code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Toaster position="top-right" />
      <nav className="navbar">
        <div className="nav-container">
          <span className="logo">🤖 AI Code Reviewer</span>
        </div>
      </nav>
      
      <main className="container">
        <h1>AI Code Reviewer</h1>
        <p className="subtitle">Upload your code and get instant feedback</p>
        
        <FileUploader onCodeLoaded={handleCodeLoaded} />
        
        {code && (
          <>
            <button 
              className="review-btn" 
              onClick={handleReview}
              disabled={loading}
            >
              {loading ? '🔍 Analyzing...' : '🚀 Review Code'}
            </button>
            <CodePreview code={code} language={language} filename={filename} />
          </>
        )}
        
        {stats && <Metrics stats={stats} summary={summary} />}
        
        {issues.length > 0 && (
          <div className="issues-section">
            <h2>🔍 Found {issues.length} Issues</h2>
            <IssueList issues={issues} code={code} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
"@ | Out-File -FilePath "frontend/src/App.js" -Encoding utf8

# Create App.css
@"
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.navbar {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.logo {
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  color: white;
  text-align: center;
  font-size: 3rem;
  margin-bottom: 1rem;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.subtitle {
  color: rgba(255,255,255,0.9);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.review-btn {
  display: block;
  width: 200px;
  margin: 2rem auto;
  padding: 1rem 2rem;
  background: white;
  border: none;
  border-radius: 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.review-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

.review-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.issues-section {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  margin-top: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
"@ | Out-File -FilePath "frontend/src/App.css" -Encoding utf8

Write-Host "✅ Frontend setup complete!" -ForegroundColor Green
Write-Host "📁 Next steps:" -ForegroundColor Yellow
Write-Host "1. cd frontend"
Write-Host "2. npm start"
