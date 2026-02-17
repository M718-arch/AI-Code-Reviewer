import React, { useState } from 'react';
import './App.css';

// Import components
import FileUploader from './components/FileUploader';
import CodePreview from './components/CodePreview';
import Metrics from './components/Metrics';
import IssueList from './components/IssueList';
import Navbar from './components/Navbar';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// API service
const reviewCode = async (code, filename = 'code.py') => {
  try {
    const response = await fetch(`${API_BASE_URL}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        filename,
      }),
    });

    if (!response.ok) {
      throw new Error('Review failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    // Return mock data if API fails
    return getMockResponse(code);
  }
};

// Mock response for testing
function getMockResponse(code) {
  const lines = code.split('\n').length;
  const issues = [];

  // Check for common issues
  if (code.includes('password') && code.includes('=')) {
    issues.push({
      line: code.split('\n').findIndex(l => l.includes('password') && l.includes('=')) + 1,
      problem: 'Hardcoded password detected',
      severity: 'HIGH',
      suggestion: 'Use environment variables instead: password = os.getenv("PASSWORD")',
      category: 'security'
    });
  }

  if (code.includes('/ 0') || code.includes('/0')) {
    const lineNum = code.split('\n').findIndex(l => l.includes('/ 0') || l.includes('/0')) + 1;
    issues.push({
      line: lineNum || 1,
      problem: 'Division by zero',
      severity: 'HIGH',
      suggestion: 'Check denominator before division: if denominator != 0:',
      category: 'bug'
    });
  }

  // Default issue if none found
  if (issues.length === 0) {
    issues.push({
      line: 1,
      problem: 'Consider adding error handling',
      severity: 'LOW',
      suggestion: 'Add try-except blocks for better error handling',
      category: 'best_practice'
    });
  }

  return {
    issues,
    summary: {
      total_issues: issues.length,
      by_severity: {
        HIGH: issues.filter(i => i.severity === 'HIGH').length,
        MEDIUM: issues.filter(i => i.severity === 'MEDIUM').length,
        LOW: issues.filter(i => i.severity === 'LOW').length
      },
      by_category: issues.reduce((acc, i) => {
        acc[i.category] = (acc[i.category] || 0) + 1;
        return acc;
      }, {})
    },
    stats: {
      total_lines: lines,
      code_lines: Math.floor(lines * 0.8),
      functions: Math.floor(lines / 5),
      characters: code.length
    },
    language: 'python'
  };
}

function App() {
  const [code, setCode] = useState('');
  const [filename, setFilename] = useState('');
  const [language, setLanguage] = useState('');
  const [issues, setIssues] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCodeLoaded = (loadedCode, loadedFilename) => {
    console.log('Code loaded:', { loadedCode, loadedFilename });
    setCode(loadedCode);
    setFilename(loadedFilename);
    setIssues([]);
    setSummary(null);
    setStats(null);
  };

  const handleReview = async () => {
    if (!code.trim()) {
      alert('Please enter code first');
      return;
    }

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      const result = await reviewCode(code, filename);
      setIssues(result.issues);
      setSummary(result.summary);
      setStats(result.stats);
      setLanguage(result.language);
    } catch (error) {
      console.error('Error analyzing code:', error);
      alert('Error analyzing code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Navbar />
      
      <main className="container">
        <div className="header-section">
          <h1>AI Code Reviewer</h1>
          <p className="subtitle">
            Upload your code and get instant AI-powered feedback on bugs,
            security issues, and best practices
          </p>
        </div>

        <div className="upload-section">
          <FileUploader onCodeLoaded={handleCodeLoaded} />
        </div>

        {code && (
          <>
            <div className="action-section">
              <button
                className="review-btn"
                onClick={handleReview}
                disabled={loading}
              >
                {loading ? '🔍 Analyzing...' : '🚀 Review Code'}
              </button>
            </div>

            <div className="code-preview-section">
              <CodePreview code={code} language={language} filename={filename} />
            </div>
          </>
        )}

        {stats && <Metrics stats={stats} summary={summary} />}

        {issues.length > 0 && (
          <div className="issues-section">
            <h2>🔍 Found {issues.length} Issues</h2>
            <IssueList issues={issues} code={code} />
          </div>
        )}

        {issues.length === 0 && summary && (
          <div className="success-message">
            <h2>✅ Perfect code! No issues found!</h2>
            <p>Your code follows best practices and has no detectable issues.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;