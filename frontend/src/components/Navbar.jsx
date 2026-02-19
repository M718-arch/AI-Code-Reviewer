import React from 'react';
import './Navbar.css';

function Navbar({ onNavigate, currentPage = 'review' }) {
  const handleNavigation = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div 
          className="nav-logo" 
          onClick={() => handleNavigation('review')}
          style={{ cursor: 'pointer' }}
        >
          <div className="terminal-dots">
            <div className="dot red"></div>
            <div className="dot yellow"></div>
            <div className="dot green"></div>
          </div>
          <span className="logo-text">
            <span className="green">code</span>
            <span className="red">_</span>
            reviewer
          </span>
        </div>

        <div className="nav-links">
          <a 
            href="#review" 
            className={`nav-link ${currentPage === 'review' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              handleNavigation('review');
            }}
          >
            review
          </a>
          <a 
            href="#docs" 
            className={`nav-link ${currentPage === 'docs' ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              handleNavigation('docs');
            }}
          >
            docs
          </a>
          <a 
            href="https://github.com/M718-arch/AI-Code-Reviewer" 
            className="nav-link github-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            github
          </a>
        </div>

        <div className="nav-right">
          <span className="version-badge">v2.0.0</span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;