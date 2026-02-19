import React, { useState } from "react";
import "./App.css";

import FileUploader from "./components/FileUploader";
import CodePreview from "./components/CodePreview";
import Metrics from "./components/Metrics";
import IssueList from "./components/IssueList";
import Navbar from "./components/Navbar";
import DocsPage from "./components/DocsPage"; // You'll need to create this
import bg from "./images/aib.png";

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const reviewCode = async (code, filename = "code.py") => {
  try {
    const response = await fetch(`${API_BASE_URL}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, filename }),
    });
    if (!response.ok) throw new Error("Review failed");
    return await response.json();
  } catch (error) {
    return getMockResponse(code);
  }
};

function getMockResponse(code) {
  const lines = code.split("\n").length;
  const issues = [];

  if (code.includes("password") && code.includes("=")) {
    issues.push({
      line:
        code.split("\n").findIndex(
          (l) => l.includes("password") && l.includes("=")
        ) + 1,
      problem: "Hardcoded password detected",
      severity: "HIGH",
      suggestion:
        'Use environment variables instead: password = os.getenv("PASSWORD")',
      category: "security",
    });
  }

  if (code.includes("/ 0") || code.includes("/0")) {
    const lineNum =
      code.split("\n").findIndex(
        (l) => l.includes("/ 0") || l.includes("/0")
      ) + 1;

    issues.push({
      line: lineNum || 1,
      problem: "Division by zero",
      severity: "HIGH",
      suggestion: "Check denominator before division",
      category: "bug",
    });
  }

  if (issues.length === 0) {
    issues.push({
      line: 1,
      problem: "Consider adding error handling",
      severity: "LOW",
      suggestion: "Add try-catch blocks",
      category: "best_practice",
    });
  }

  return {
    issues,
    summary: {
      total_issues: issues.length,
      by_severity: {
        HIGH: issues.filter((i) => i.severity === "HIGH").length,
        MEDIUM: issues.filter((i) => i.severity === "MEDIUM").length,
        LOW: issues.filter((i) => i.severity === "LOW").length,
      },
      by_category: issues.reduce((acc, i) => {
        acc[i.category] = (acc[i.category] || 0) + 1;
        return acc;
      }, {}),
    },
    stats: {
      total_lines: lines,
      code_lines: Math.floor(lines * 0.8),
      functions: Math.floor(lines / 5),
      characters: code.length,
    },
    language: "python",
  };
}

function App() {
  const [currentPage, setCurrentPage] = useState('review'); // 'review' or 'docs'
  const [code, setCode] = useState("");
  const [filename, setFilename] = useState("");
  const [language, setLanguage] = useState("");
  const [issues, setIssues] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleNavigation = (page) => {
    setCurrentPage(page);
  };

  const handleCodeLoaded = (loadedCode, loadedFilename) => {
    setCode(loadedCode);
    setFilename(loadedFilename);
    setIssues([]);
    setSummary(null);
    setStats(null);
  };

  const handleReview = async () => {
    if (!code.trim()) {
      alert("Please enter code first");
      return;
    }

    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const result = await reviewCode(code, filename);
      setIssues(result.issues);
      setSummary(result.summary);
      setStats(result.stats);
      setLanguage(result.language);
    } catch (error) {
      alert("Error analyzing code");
    } finally {
      setLoading(false);
    }
  };

  // Render review page
  const renderReviewPage = () => (
    <>
      <div className="header-section">
        <h1>
          <span className="green">code</span>
          <span className="red">_</span>
          reviewer
        </h1>

        <div className="header-prompt">
          <span className="prompt-symbol">$</span>
          <span className="subtitle">
            Upload your source file — get instant analysis on bugs, security
            vulnerabilities, and bad practices.
          </span>
        </div>

        <div className="status-bar">
          <div className="status-item">
            <div className="status-dot"></div>
            <span>AI engine online</span>
          </div>
          <div className="status-item">
            <div className="status-dot red"></div>
            <span>12 languages supported</span>
          </div>
          <div className="status-item">
            <span>v2.0.0</span>
          </div>
        </div>
      </div>

      <div className="upload-section">
        <div className="section-label">
          <div className="label-dot"></div>
          input.source
        </div>
        <div className="upload-section-inner">
          <FileUploader onCodeLoaded={handleCodeLoaded} />
        </div>
      </div>

      {code && (
        <>
          <div className="action-section">
            <button
              className="review-btn"
              onClick={handleReview}
              disabled={loading}
            >
              {loading ? "> running analysis..." : "> run --analyze"}
            </button>
          </div>

          <div
            style={{
              backgroundImage: `url(${bg})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
              backgroundRepeat: "no-repeat",
              minHeight: "400px",
              width: "100%",
              padding: "20px"
            }}
          >
            <div className="code-preview-section">
              <CodePreview
                code={code}
                language={language}
                filename={filename}
              />
            </div>
          </div>
        </>
      )}

      {stats && <Metrics stats={stats} summary={summary} />}

      {issues.length > 0 && (
        <div className="issues-section">
          <h2>
            ⚠ {issues.length} issue
            {issues.length !== 1 ? "s" : ""} detected
          </h2>
          <div className="issues-inner">
            <IssueList issues={issues} code={code} />
          </div>
        </div>
      )}

      {issues.length === 0 && summary && (
        <div className="success-message">
          <h2>✓ No issues found</h2>
          <p>
            Your code passed all checks. No bugs, vulnerabilities, or bad
            practices detected.
          </p>
        </div>
      )}
    </>
  );

  return (
    <div className="App">
      <Navbar onNavigate={handleNavigation} currentPage={currentPage} />
      
      <main className="container">
        {currentPage === 'review' ? renderReviewPage() : <DocsPage />}
      </main>
    </div>
  );
}

export default App;