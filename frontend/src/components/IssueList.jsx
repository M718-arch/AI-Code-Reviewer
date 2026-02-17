import React, { useState } from 'react';
import './IssueList.css';
import { FiAlertTriangle, FiAlertCircle, FiInfo, FiChevronDown, FiChevronUp } from 'react-icons/fi';

function IssueList({ issues, code }) {
  const [expandedIssue, setExpandedIssue] = useState(null);

  const getSeverityIcon = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH':
        return <FiAlertCircle className="severity-icon high" />;
      case 'MEDIUM':
        return <FiAlertTriangle className="severity-icon medium" />;
      default:
        return <FiInfo className="severity-icon low" />;
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'HIGH': return 'high';
      case 'MEDIUM': return 'medium';
      default: return 'low';
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
              <span className="issue-line">Line {issue.line}</span>
              <span className="issue-problem">{issue.problem}</span>
            </div>
            <div className="issue-meta">
              <span className="issue-severity">{issue.severity}</span>
              <span className="issue-category">{issue.category}</span>
              {expandedIssue === index ? <FiChevronUp /> : <FiChevronDown />}
            </div>
          </div>

          {expandedIssue === index && (
            <div className="issue-details">
              <div className="issue-suggestion">
                <strong>💡 Suggestion:</strong> {issue.suggestion}
              </div>

              {issue.line && (
                <div className="issue-code">
                  <strong>📄 Code at line {issue.line}:</strong>
                  <pre>
                    <code>{getLineCode(issue.line)}</code>
                  </pre>
                </div>
              )}

              <button className="fix-btn" onClick={(e) => {
                e.stopPropagation();
                alert(`Fix: ${issue.suggestion}`);
              }}>
                🔧 Show Fix
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default IssueList;