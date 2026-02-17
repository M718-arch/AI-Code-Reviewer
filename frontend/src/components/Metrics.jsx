import React from 'react';
import './Metrics.css';
import { FiCode, FiFile, FiCpu, FiAlertCircle } from 'react-icons/fi';

function Metrics({ stats, summary }) {
  if (!stats || !summary) return null;

  const metrics = [
    {
      icon: <FiFile />,
      label: 'Total Lines',
      value: stats.total_lines,
      color: '#667eea'
    },
    {
      icon: <FiCode />,
      label: 'Code Lines',
      value: stats.code_lines,
      color: '#48bb78'
    },
    {
      icon: <FiCpu />,
      label: 'Functions',
      value: stats.functions,
      color: '#ed8936'
    },
    {
      icon: <FiAlertCircle />,
      label: 'Issues',
      value: summary.total_issues,
      color: '#f56565'
    }
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((metric, index) => (
        <div key={index} className="metric-card">
          <div className="metric-icon" style={{ background: `${metric.color}20`, color: metric.color }}>
            {metric.icon}
          </div>
          <div className="metric-content">
            <span className="metric-label">{metric.label}</span>
            <span className="metric-value">{metric.value}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default Metrics;