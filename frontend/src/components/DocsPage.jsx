import React from 'react';
import './DocsPage.css';

function DocsPage() {
  return (
    <div className="docs-container">
      <div className="docs-header">
        <h1>
          <span className="green">documentation</span>
          <span className="red">.md</span>
        </h1>
        <div className="header-prompt">
          <span className="prompt-symbol">$</span>
          <span className="subtitle">
            Learn how to use Code Reviewer effectively
          </span>
        </div>
      </div>

      <div className="docs-grid">
        {/* Quick Start */}
        <section className="docs-section">
          <h2>
            <span className="prompt-symbol">#</span>
            quick_start
          </h2>
          <div className="docs-content">
            <p>Get started with Code Reviewer in 3 simple steps:</p>
            <ol className="steps-list">
              <li>Upload your source code file</li>
              <li>Click "run --analyze" to start the review</li>
              <li>Review the issues and suggestions</li>
            </ol>
          </div>
        </section>

        {/* API Reference */}
        <section className="docs-section">
          <h2>
            <span className="prompt-symbol">#</span>
            api_reference
          </h2>
          <div className="docs-content">
            <h3>POST /api/review</h3>
            <div className="code-block">
              <pre>
{`{
  "code": "your source code here",
  "filename": "example.py"
}`}
              </pre>
            </div>

            <h3>Response Format</h3>
            <div className="code-block">
              <pre>
{`{
  "issues": [
    {
      "line": 10,
      "problem": "Description",
      "severity": "HIGH",
      "suggestion": "How to fix",
      "category": "bug"
    }
  ],
  "summary": {...},
  "stats": {...},
  "language": "python"
}`}
              </pre>
            </div>
          </div>
        </section>

        {/* Supported Languages */}
        <section className="docs-section">
          <h2>
            <span className="prompt-symbol">#</span>
            supported_languages
          </h2>
          <div className="docs-content">
            <div className="language-grid">
              {[
                'Python', 'JavaScript', 'TypeScript', 'Java',
                'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
                'Swift', 'Kotlin'
              ].map(lang => (
                <div key={lang} className="language-card">
                  <span className="language-name">{lang}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Issue Categories */}
        <section className="docs-section">
          <h2>
            <span className="prompt-symbol">#</span>
            issue_categories
          </h2>
          <div className="docs-content">
            <div className="categories-grid">
              <div className="category-card">
                <h3>🐛 Bug Detection</h3>
                <ul>
                  <li>Division by zero</li>
                  <li>Undefined variables</li>
                  <li>Type errors</li>
                  <li>Infinite recursion</li>
                </ul>
              </div>
              <div className="category-card">
                <h3>🔒 Security</h3>
                <ul>
                  <li>Hardcoded secrets</li>
                  <li>SQL injection risks</li>
                  <li>Command injection</li>
                  <li>Insecure defaults</li>
                </ul>
              </div>
              <div className="category-card">
                <h3>🎨 Best Practices</h3>
                <ul>
                  <li>Error handling</li>
                  <li>Code complexity</li>
                  <li>Naming conventions</li>
                  <li>Documentation</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Severity Levels */}
        <section className="docs-section">
          <h2>
            <span className="prompt-symbol">#</span>
            severity_levels
          </h2>
          <div className="docs-content">
            <div className="severity-list">
              <div className="severity-item high">
                <span className="severity-badge">HIGH</span>
                <span className="severity-desc">Critical issues that must be fixed</span>
              </div>
              <div className="severity-item medium">
                <span className="severity-badge">MEDIUM</span>
                <span className="severity-desc">Should be addressed soon</span>
              </div>
              <div className="severity-item low">
                <span className="severity-badge">LOW</span>
                <span className="severity-desc">Suggestions for improvement</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default DocsPage;