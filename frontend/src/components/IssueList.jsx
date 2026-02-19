import React, { useState } from 'react';
import './IssueList.css';

function IssueList({ issues, code }) {
  const [expandedIssue, setExpandedIssue] = useState(null);

  const getSeverityIcon = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH':   return <span className="severity-icon high">✗</span>;
      case 'MEDIUM': return <span className="severity-icon medium">△</span>;
      default:       return <span className="severity-icon low">◦</span>;
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH':   return 'high';
      case 'MEDIUM': return 'medium';
      default:       return 'low';
    }
  };

  const getLineCode = (lineNumber) => {
    const lines = code.split('\n');
    return lines[lineNumber - 1] || '';
  };

  const toggleIssue = (index) => {
    setExpandedIssue(expandedIssue === index ? null : index);
  };

  return (
    <div className="issue-list">
      {issues.map((issue, index) => (
        <div
          key={index}
          className={`issue-card ${getSeverityClass(issue.severity)}`}
          onClick={() => toggleIssue(index)}
        >
          <div className="issue-header">
            <div className="issue-title">
              {getSeverityIcon(issue.severity)}
              <span className="issue-line">ln:{issue.line}</span>
              <span className="issue-problem">{issue.problem}</span>
            </div>
            <div className="issue-meta">
              <span className="issue-severity">{issue.severity}</span>
              <span className="issue-category">{issue.category}</span>
              <span className={`issue-toggle ${expandedIssue === index ? 'open' : ''}`}>▾</span>
            </div>
          </div>

          {expandedIssue === index && (
            <div className="issue-details">
              <div className="issue-suggestion">
                <strong>→ suggestion:</strong> {issue.suggestion}
              </div>

              {issue.line && (
                <div className="issue-code">
                  <strong>source at line {issue.line}:</strong>
                  <pre><code>{getLineCode(issue.line)}</code></pre>
                </div>
              )}

              <button
                className="fix-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  alert(`Fix: ${issue.suggestion}`);
                }}
              >
                → apply fix
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default IssueList;