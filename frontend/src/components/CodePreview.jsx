import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodePreview.css';

// Override vscDarkPlus to match our theme
const terminalTheme = {
  ...vscDarkPlus,
  'pre[class*="language-"]': {
    ...vscDarkPlus['pre[class*="language-"]'],
    background: '#0d0d0d',
    margin: 0,
    borderRadius: 0,
    fontSize: '0.83rem',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  },
  'code[class*="language-"]': {
    ...vscDarkPlus['code[class*="language-"]'],
    background: 'none',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  },
};

function CodePreview({ code, language, filename }) {
  return (
    <div className="code-preview">
      <div className="preview-header">
        <div className="preview-title-group">
          <div className="preview-dot"></div>
          <span className="filename">{filename || 'untitled'}</span>
        </div>
        <div className="preview-meta">
          <span className="language-badge">{language || 'text'}</span>
        </div>
      </div>
      <SyntaxHighlighter
        language={language || 'text'}
        style={terminalTheme}
        showLineNumbers
        wrapLines
        lineNumberStyle={{
          color: '#333',
          fontSize: '0.75rem',
          minWidth: '3em',
          paddingRight: '1em',
          userSelect: 'none',
        }}
        customStyle={{
          margin: 0,
          borderRadius: 0,
          fontSize: '0.83rem',
          lineHeight: '1.65',
          maxHeight: '420px',
          overflow: 'auto',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

export default CodePreview;