import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodePreview.css';

function CodePreview({ code, language, filename }) {
  return (
    <div className="code-preview">
      <div className="preview-header">
        <span className="filename">{filename || 'code.py'}</span>
        <span className="language-badge">{language || 'python'}</span>
      </div>
      <SyntaxHighlighter
        language={language || 'python'}
        style={vscDarkPlus}
        showLineNumbers
        wrapLines
        customStyle={{
          margin: 0,
          borderRadius: '0 0 1rem 1rem',
          fontSize: '0.9rem',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

export default CodePreview;