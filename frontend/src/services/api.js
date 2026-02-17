// API service
const API_BASE_URL = 'http://localhost:8000/api';

export const reviewCode = async (code, filename = null, useAI = true) => {
  try {
    const response = await fetch(`${API_BASE_URL}/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        filename,
        use_ai: useAI,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Review failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return getMockResponse(code);
  }
};

export const uploadFile = async (file, useAI = true) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('use_ai', useAI);
  
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const code = e.target.result;
        resolve({
          code,
          ...getMockResponse(code)
        });
      };
      reader.readAsText(file);
    });
  }
};

// New function to fetch from GitHub
export const fetchFromGithub = async (url) => {
  try {
    // Convert github.com to raw.githubusercontent.com
    let rawUrl = url
      .replace('github.com', 'raw.githubusercontent.com')
      .replace('/blob/', '/');

    // If it's already a raw URL, use it as is
    if (url.includes('raw.githubusercontent.com')) {
      rawUrl = url;
    }

    const response = await fetch(rawUrl);
    if (!response.ok) {
      throw new Error('Failed to fetch from GitHub');
    }

    const code = await response.text();
    const filename = url.split('/').pop() || 'github_code.py';
    
    return {
      code,
      filename,
      ...getMockResponse(code)
    };
  } catch (error) {
    console.error('GitHub fetch error:', error);
    throw error;
  }
};

// Mock response for testing
function getMockResponse(code) {
  const lines = code.split('\n').length;
  
  // Generate mock issues based on code content
  const issues = [];
  
  if (code.includes('password') && code.includes('=')) {
    issues.push({
      line: code.split('\n').findIndex(l => l.includes('password') && l.includes('=')) + 1,
      problem: 'Hardcoded password detected',
      severity: 'HIGH',
      suggestion: 'Use environment variables instead: password = os.getenv("PASSWORD")',
      category: 'security'
    });
  }
  
  if (code.includes('/ 0') || code.includes('/0')) {
    const lineNum = code.split('\n').findIndex(l => l.includes('/ 0') || l.includes('/0')) + 1;
    issues.push({
      line: lineNum || 1,
      problem: 'Division by zero',
      severity: 'HIGH',
      suggestion: 'Check denominator before division: if denominator != 0:',
      category: 'bug'
    });
  }
  
  // Check for unclosed strings
  const lines_array = code.split('\n');
  lines_array.forEach((line, index) => {
    if ((line.match(/"/g) || []).length % 2 !== 0 || (line.match(/'/g) || []).length % 2 !== 0) {
      issues.push({
        line: index + 1,
        problem: 'Unclosed string',
        severity: 'HIGH',
        suggestion: 'Add closing quote at the end of the line',
        category: 'syntax'
      });
    }
  });
  
  // Check for missing colons
  lines_array.forEach((line, index) => {
    const stripped = line.trim();
    if (stripped.startsWith('if ') || stripped.startsWith('for ') || 
        stripped.startsWith('while ') || stripped.startsWith('def ')) {
      if (!stripped.endsWith(':')) {
        issues.push({
          line: index + 1,
          problem: 'Missing colon',
          severity: 'HIGH',
          suggestion: "Add ':' at the end of the line",
          category: 'syntax'
        });
      }
    }
  });
  
  // If no issues found, add a default one for demo
  if (issues.length === 0) {
    issues.push({
      line: 1,
      problem: 'Consider adding error handling',
      severity: 'LOW',
      suggestion: 'Add try-except blocks for better error handling',
      category: 'best_practice'
    });
  }

  return {
    issues,
    summary: {
      total_issues: issues.length,
      by_severity: {
        HIGH: issues.filter(i => i.severity === 'HIGH').length,
        MEDIUM: issues.filter(i => i.severity === 'MEDIUM').length,
        LOW: issues.filter(i => i.severity === 'LOW').length
      },
      by_category: issues.reduce((acc, i) => {
        acc[i.category] = (acc[i.category] || 0) + 1;
        return acc;
      }, {})
    },
    stats: {
      total_lines: lines,
      code_lines: Math.floor(lines * 0.8),
      functions: Math.floor(lines / 5),
      characters: code.length
    },
    language: 'python'
  };
}