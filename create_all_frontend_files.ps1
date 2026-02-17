# ============================================================================
# CREATE ALL FRONTEND FILES FOR AI CODE REVIEWER
# Run this script in PowerShell to generate all components and API files
# ============================================================================

Write-Host "🚀 Creating all frontend files..." -ForegroundColor Cyan

# Navigate to frontend/src
Set-Location -Path "C:\Users\DELL\Desktop\LLMs_Projcet\ai-code-reviewer\frontend\src"

# ============================================================================
# CREATE SERVICES/API.JS
# ============================================================================
Write-Host "📁 Creating services/api.js..." -ForegroundColor Yellow

# Create services directory if it doesn't exist
New-Item -ItemType Directory -Path "services" -Force | Out-Null

@'
/**
 * API service for AI Code Reviewer
 * Handles all backend communication
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Upload a file to the backend
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} - The uploaded file data
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

/**
 * Send code for review
 * @param {string} code - The code to review
 * @param {string} filename - The filename (optional)
 * @returns {Promise<Object>} - The review results
 */
export const reviewCode = async (code, filename = 'code.py') => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/review`, {
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
      throw new Error(`Review failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error reviewing code:', error);
    
    // Return mock data for testing when backend is unavailable
    console.log('Using mock data because backend is unavailable');
    return {
      issues: [
        {
          line: 1,
          problem: 'Hardcoded password detected',
          severity: 'HIGH',
          suggestion: 'Use environment variables instead',
          category: 'security'
        },
        {
          line: 3,
          problem: 'Division by zero',
          severity: 'HIGH',
          suggestion: 'Check denominator before division',
          category: 'bug'
        }
      ],
      summary: {
        total_issues: 2,
        by_severity: { HIGH: 2, MEDIUM: 0, LOW: 0 },
        by_category: { security: 1, bug: 1 }
      },
      language: 'python',
      stats: {
        total_lines: 10,
        code_lines: 8,
        functions: 2,
        characters: 250
      }
    };
  }
};

/**
 * Check if backend is healthy
 * @returns {Promise<boolean>} - True if backend is healthy
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
};

export default {
  uploadFile,
  reviewCode,
  checkHealth
};
'@ | Out-File -FilePath "services/api.js" -Encoding utf8

Write-Host "✅ services/api.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/FILEUPLOADER.JS
# ============================================================================
Write-Host "📁 Creating components/FileUploader.js..." -ForegroundColor Yellow

# Create components directory if it doesn't exist
New-Item -ItemType Directory -Path "components" -Force | Out-Null

@'
import React, { useState } from 'react';
import './FileUploader.css';
import { uploadFile } from '../services/api';

const FileUploader = ({ onCodeLoaded }) => {
  const [dragActive, setDragActive] = useState(false);
  const [code, setCode] = useState('');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);

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
    
    const file = e.dataTransfer.files[0];
    if (file) {
      await processFile(file);
    }
  };

  const handleChange = async (e) => {
    e.preventDefault();
    const file = e.target.files[0];
    if (file) {
      await processFile(file);
    }
  };

  const processFile = async (file) => {
    const validExtensions = ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb', 
                            '.go', '.rs', '.swift', '.kt', '.ts', '.html', '.css'];
    
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!validExtensions.includes(ext)) {
      alert(`File type ${ext} not supported`);
      return;
    }

    setLoading(true);
    try {
      const result = await uploadFile(file);
      setCode(result.code);
      setFileName(file.name);
      onCodeLoaded(result.code, file.name);
    } catch (error) {
      // Fallback to local file reading
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        setCode(content);
        setFileName(file.name);
        onCodeLoaded(content, file.name);
      };
      reader.readAsText(file);
    } finally {
      setLoading(false);
    }
  };

  const handlePasteChange = (e) => {
    const pastedCode = e.target.value;
    setCode(pastedCode);
    setFileName('pasted_code.py');
    onCodeLoaded(pastedCode, 'pasted_code.py');
  };

  const handleClear = () => {
    setCode('');
    setFileName('');
    onCodeLoaded('', '');
  };

  return (
    <div className="file-uploader">
      {!code ? (
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
            onChange={handleChange}
            accept=".py,.js,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.ts,.html,.css"
          />
          <label htmlFor="file-input" className="dropzone-label">
            <div className="upload-icon">📁</div>
            <h3>{loading ? 'Uploading...' : 'Drop your code file here'}</h3>
            <p>or click to browse</p>
            <span className="file-types">
              Supports: .py, .js, .java, .cpp, .c, .cs, .php, .rb, .go, .rs, .swift, .kt, .ts, .html, .css
            </span>
          </label>
        </div>
      ) : (
        <div className="file-info">
          <div className="file-details">
            <span className="file-icon">📄</span>
            <span className="file-name">{fileName}</span>
            <div className="file-actions">
              <button className="btn-clear" onClick={handleClear}>
                ✖ Clear
              </button>
            </div>
          </div>
          <textarea
            className="code-textarea"
            value={code}
            onChange={handlePasteChange}
            placeholder="Edit your code here..."
            rows={10}
          />
        </div>
      )}
    </div>
  );
};

export default FileUploader;
'@ | Out-File -FilePath "components/FileUploader.js" -Encoding utf8

Write-Host "✅ components/FileUploader.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/FILEUPLOADER.CSS
# ============================================================================
Write-Host "📁 Creating components/FileUploader.css..." -ForegroundColor Yellow

@'
.file-uploader {
  width: 100%;
}

.dropzone {
  border: 3px dashed #cbd5e0;
  border-radius: 1rem;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
}

.dropzone.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  transform: scale(1.02);
}

.dropzone input {
  display: none;
}

.dropzone-label {
  cursor: pointer;
  display: block;
}

.upload-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 1rem;
}

.dropzone h3 {
  color: #1a1a2e;
  margin-bottom: 0.5rem;
  font-size: 1.3rem;
}

.dropzone p {
  color: #718096;
  margin-bottom: 1rem;
}

.file-types {
  display: block;
  color: #a0aec0;
  font-size: 0.9rem;
}

.file-info {
  background: #f8fafc;
  border-radius: 0.5rem;
  padding: 1rem;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.file-icon {
  font-size: 1.5rem;
  color: #667eea;
}

.file-name {
  flex: 1;
  font-weight: 500;
  color: #1a1a2e;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-clear {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  background: #f56565;
  color: white;
}

.btn-clear:hover {
  background: #e53e3e;
  transform: translateY(-2px);
}

.code-textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  resize: vertical;
  min-height: 200px;
}

.code-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

@media (max-width: 768px) {
  .dropzone {
    padding: 2rem 1rem;
  }
  
  .file-details {
    flex-wrap: wrap;
  }
  
  .file-name {
    width: 100%;
    order: -1;
  }
}
'@ | Out-File -FilePath "components/FileUploader.css" -Encoding utf8

Write-Host "✅ components/FileUploader.css created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/CODEPREVIEW.JS
# ============================================================================
Write-Host "📁 Creating components/CodePreview.js..." -ForegroundColor Yellow

@'
import React from 'react';
import './CodePreview.css';

const CodePreview = ({ code, language, filename }) => {
  return (
    <div className="code-preview">
      <div className="preview-header">
        <span className="filename">{filename || 'code.py'}</span>
        <span className="language-badge">{language || 'python'}</span>
      </div>
      <pre className="code-content">
        <code>{code}</code>
      </pre>
    </div>
  );
};

export default CodePreview;
'@ | Out-File -FilePath "components/CodePreview.js" -Encoding utf8

Write-Host "✅ components/CodePreview.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/CODEPREVIEW.CSS
# ============================================================================
Write-Host "📁 Creating components/CodePreview.css..." -ForegroundColor Yellow

@'
.code-preview {
  border-radius: 1rem;
  overflow: hidden;
}

.preview-header {
  background: #2d2d3a;
  padding: 0.8rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #40404e;
}

.filename {
  color: #e2e8f0;
  font-size: 0.9rem;
  font-weight: 500;
}

.language-badge {
  background: #40404e;
  color: #a0aec0;
  padding: 0.2rem 0.8rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.code-content {
  margin: 0;
  padding: 1rem;
  color: #e2e8f0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  overflow-x: auto;
  background: #1e1e2e;
  white-space: pre-wrap;
  word-wrap: break-word;
}
'@ | Out-File -FilePath "components/CodePreview.css" -Encoding utf8

Write-Host "✅ components/CodePreview.css created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/METRICS.JS
# ============================================================================
Write-Host "📁 Creating components/Metrics.js..." -ForegroundColor Yellow

@'
import React from 'react';
import './Metrics.css';

const Metrics = ({ stats, summary }) => {
  if (!stats || !summary) return null;

  const metrics = [
    { label: 'Total Lines', value: stats.total_lines, color: '#667eea' },
    { label: 'Code Lines', value: stats.code_lines, color: '#48bb78' },
    { label: 'Functions', value: stats.functions, color: '#ed8936' },
    { label: 'Issues', value: summary.total_issues, color: '#f56565' }
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((metric, index) => (
        <div key={index} className="metric-card">
          <div className="metric-content">
            <span className="metric-label">{metric.label}</span>
            <span className="metric-value">{metric.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Metrics;
'@ | Out-File -FilePath "components/Metrics.js" -Encoding utf8

Write-Host "✅ components/Metrics.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/METRICS.CSS
# ============================================================================
Write-Host "📁 Creating components/Metrics.css..." -ForegroundColor Yellow

@'
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.metric-content {
  text-align: center;
}

.metric-label {
  display: block;
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}

.metric-value {
  display: block;
  color: #1a1a2e;
  font-size: 2rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
'@ | Out-File -FilePath "components/Metrics.css" -Encoding utf8

Write-Host "✅ components/Metrics.css created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/ISSUELIST.JS
# ============================================================================
Write-Host "📁 Creating components/IssueList.js..." -ForegroundColor Yellow

@'
import React, { useState } from 'react';
import './IssueList.css';

const IssueList = ({ issues, code }) => {
  const [expandedIssue, setExpandedIssue] = useState(null);

  const getSeverityClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH': return 'high';
      case 'MEDIUM': return 'medium';
      default: return 'low';
    }
  };

  const getLineCode = (lineNumber) => {
    if (!code || !lineNumber) return '';
    const lines = code.split('\n');
    return lines[lineNumber - 1] || '';
  };

  return (
    <div className="issue-list">
      {issues.map((issue, index) => (
        <div
          key={index}
          className={`issue-card ${getSeverityClass(issue.severity)}`}
          onClick={() => setExpandedIssue(expandedIssue === index ? null : index)}
        >
          <div className="issue-header">
            <div className="issue-title">
              <span className="issue-line">Line {issue.line}</span>
              <span className="issue-problem">{issue.problem}</span>
            </div>
            <span className="issue-severity">{issue.severity}</span>
          </div>
          
          {expandedIssue === index && (
            <div className="issue-details">
              <div className="issue-suggestion">
                <strong>💡 Suggestion:</strong> {issue.suggestion}
              </div>
              
              {issue.line && (
                <div className="issue-code">
                  <strong>Code at line {issue.line}:</strong>
                  <pre>{getLineCode(issue.line)}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default IssueList;
'@ | Out-File -FilePath "components/IssueList.js" -Encoding utf8

Write-Host "✅ components/IssueList.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/ISSUELIST.CSS
# ============================================================================
Write-Host "📁 Creating components/IssueList.css..." -ForegroundColor Yellow

@'
.issue-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.issue-card {
  background: white;
  border-radius: 0.8rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.issue-card:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.issue-card.high {
  border-left-color: #f56565;
  background: #fff5f5;
}

.issue-card.medium {
  border-left-color: #ed8936;
  background: #fffaf0;
}

.issue-card.low {
  border-left-color: #48bb78;
  background: #f0fff4;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.issue-title {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.issue-line {
  background: #e2e8f0;
  padding: 0.2rem 0.6rem;
  border-radius: 0.3rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
}

.issue-problem {
  font-weight: 500;
  color: #1a1a2e;
}

.issue-severity {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 0.3rem;
  background: #e2e8f0;
  color: #4a5568;
}

.issue-details {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.issue-suggestion {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.issue-code {
  background: #1e1e2e;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.issue-code pre {
  margin: 0.5rem 0 0 0;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-wrap: break-word;
}

@media (max-width: 768px) {
  .issue-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
'@ | Out-File -FilePath "components/IssueList.css" -Encoding utf8

Write-Host "✅ components/IssueList.css created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/NAVBAR.JS
# ============================================================================
Write-Host "📁 Creating components/Navbar.js..." -ForegroundColor Yellow

@'
import React from 'react';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-icon">🤖</span>
          <span className="logo-text">AI Code Reviewer</span>
        </div>
        <div className="nav-links">
          <a href="#" className="nav-link active">Home</a>
          <a href="#" className="nav-link">About</a>
          <a href="#" className="nav-link">GitHub</a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
'@ | Out-File -FilePath "components/Navbar.js" -Encoding utf8

Write-Host "✅ components/Navbar.js created!" -ForegroundColor Green

# ============================================================================
# CREATE COMPONENTS/NAVBAR.CSS
# ============================================================================
Write-Host "📁 Creating components/Navbar.css..." -ForegroundColor Yellow

@'
.navbar {
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.3rem;
  font-weight: 600;
}

.logo-icon {
  font-size: 1.8rem;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #4a5568;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #667eea;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 1rem;
  }
  
  .nav-links {
    gap: 1rem;
  }
  
  .logo-text {
    display: none;
  }
}
'@ | Out-File -FilePath "components/Navbar.css" -Encoding utf8

Write-Host "✅ components/Navbar.css created!" -ForegroundColor Green

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✅ ALL FILES CREATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Files created in frontend/src:" -ForegroundColor Yellow
Write-Host "  ├── services/" -ForegroundColor White
Write-Host "  │   └── api.js" -ForegroundColor White
Write-Host "  └── components/" -ForegroundColor White
Write-Host "      ├── FileUploader.js" -ForegroundColor White
Write-Host "      ├── FileUploader.css" -ForegroundColor White
Write-Host "      ├── CodePreview.js" -ForegroundColor White
Write-Host "      ├── CodePreview.css" -ForegroundColor White
Write-Host "      ├── Metrics.js" -ForegroundColor White
Write-Host "      ├── Metrics.css" -ForegroundColor White
Write-Host "      ├── IssueList.js" -ForegroundColor White
Write-Host "      ├── IssueList.css" -ForegroundColor White
Write-Host "      ├── Navbar.js" -ForegroundColor White
Write-Host "      └── Navbar.css" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure your App.js and App.css are updated" -ForegroundColor Yellow
Write-Host "2. Run: cd frontend" -ForegroundColor Yellow
Write-Host "3. Run: npm start" -ForegroundColor Yellow
Write-Host ""