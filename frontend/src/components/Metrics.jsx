import React from 'react';
import './Metrics.css';

function Metrics({ stats, summary }) {
  if (!stats || !summary) return null;

  const metrics = [
    {
      icon: '▤',
      label: 'total_lines',
      value: stats.total_lines,
      colorClass: 'white',
      accent: '#f0f0f0',
      sub: 'lines of code',
    },
    {
      icon: '{ }',
      label: 'code_lines',
      value: stats.code_lines,
      colorClass: 'green',
      accent: '#00ff88',
      sub: 'executable lines',
    },
    {
      icon: 'ƒ',
      label: 'functions',
      value: stats.functions,
      colorClass: 'white',
      accent: '#f0f0f0',
      sub: 'detected functions',
    },
    {
      icon: '⚠',
      label: 'issues',
      value: summary.total_issues,
      colorClass: summary.total_issues === 0 ? 'green' : 'red',
      accent: summary.total_issues === 0 ? '#00ff88' : '#ff3333',
      sub: summary.total_issues === 0 ? 'no issues found' : 'require attention',
    },
  ];

  return (
    <div className="metrics-wrapper">
      <div className="metrics-header">
        output.stats
      </div>
      <div className="metrics-grid">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className="metric-card"
            style={{ '--accent-color': metric.accent }}
          >
            <div className="metric-icon">{metric.icon}</div>
            <div className="metric-label">{metric.label}</div>
            <div className={`metric-value ${metric.colorClass}`}>
              {metric.value}
            </div>
            <div className="metric-sub">{metric.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Metrics;