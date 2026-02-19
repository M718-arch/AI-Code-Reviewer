# AI Code Reviewer 🔍

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.x-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&duration=3000&pause=1000&color=00FF9D&center=true&vCenter=true&width=435&lines=41+Analysis+Engines;12+Languages+Supported;Real-time+Code+Review;Terminal+Inspired+UI" alt="Typing SVG" />

**A powerful, terminal-inspired code analysis tool that helps developers identify bugs, security vulnerabilities, and bad practices in their code.**

[Installation](#-quick-start) • [Features](#-features) • [API](#-api-documentation) • [Testing](#-testing) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Analysis Engine](#-analysis-engine)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔍 Multi-Language Support
| Language | File Extensions | Detection Method |
|----------|----------------|------------------|
| Python | .py | AST parsing + regex |
| JavaScript | .js, .jsx | Pattern matching |
| TypeScript | .ts, .tsx | Pattern matching |
| Java | .java | Pattern matching |
| C/C++ | .cpp, .c, .h | Pattern matching |
| C# | .cs | Pattern matching |
| PHP | .php | Pattern matching |
| Ruby | .rb | Pattern matching |
| Go | .go | Pattern matching |
| Rust | .rs | Pattern matching |
| Swift | .swift | Pattern matching |
| Kotlin | .kt | Pattern matching |
| HTML | .html, .htm | Pattern matching |
| CSS | .css | Pattern matching |

### 🐛 Bug Detection (41 Analysis Engines)
| Category | Issues Detected |
|----------|-----------------|
| **Syntax Errors** | AST parsing, unclosed strings, missing colons, invalid escape sequences, smart quotes |
| **Undefined Variables** | Scope-aware analysis, imports tracking, built-ins detection |
| **Math Errors** | Division by zero, integer overflow, modulo by zero |
| **Type Errors** | String + int concatenation, list + string, dict key type mismatches |
| **Index Errors** | List index out of range, string index errors, slice errors |
| **Key Errors** | Missing dictionary keys, nested key access |
| **Attribute Errors** | NoneType attributes, invalid method calls, missing properties |
| **Recursion Issues** | Infinite recursion, missing base cases, stack overflow risks |

### 🔒 Security Scanning
| Issue | Detection Method | Severity |
|-------|-----------------|----------|
| Hardcoded passwords | Regex pattern matching | 🔴 HIGH |
| Hardcoded API keys | Keyword detection | 🔴 HIGH |
| Hardcoded tokens | Pattern recognition | 🔴 HIGH |
| SQL injection | Raw query detection | 🔴 HIGH |
| Command injection | Shell command patterns | 🔴 HIGH |
| Path traversal | File path patterns | 🔴 HIGH |
| Bare except clauses | AST analysis | 🔴 HIGH |
| File operations w/o checks | Pattern matching | 🟡 MEDIUM |
| Insecure deserialization | Pickle/yaml detection | 🔴 HIGH |
| Weak cryptography | MD5, SHA1 detection | 🔴 HIGH |

### 🎨 Best Practices
| Issue | Detection | Severity |
|-------|-----------|----------|
| Mutable default arguments | AST analysis | 🟡 MEDIUM |
| Wildcard imports | AST analysis | 🟡 MEDIUM |
| Empty except blocks | AST analysis | 🟡 MEDIUM |
| Redefining built-ins | AST + builtins list | 🟡 MEDIUM |
| Missing self in methods | AST class analysis | 🔴 HIGH |
| Comparing None with == | AST comparison check | 🟢 LOW |
| Using 'is' with literals | AST is operator check | 🟢 LOW |
| Too many arguments (>7) | Function signature | 🟡 MEDIUM |
| Long functions (>80 lines) | Line count | 🟡 MEDIUM |
| Long lines (>120 chars) | Line length | 🟢 LOW |
| TODO/FIXME comments | Regex pattern | 🟢 LOW |
| Unused variables | AST variable tracking | 🟢 LOW |
| Unused imports | AST import tracking | 🟢 LOW |
| Missing docstrings | AST function/class check | 🟢 LOW |
| Variable naming conventions | Regex patterns | 🟢 LOW |

### 📊 Detailed Metrics
```json
{
  "stats": {
    "total_lines": 150,
    "code_lines": 120,
    "functions": 8,
    "classes": 2,
    "characters": 4500,
    "complexity_score": 24.5
  },
  "summary": {
    "total_issues": 5,
    "by_severity": {
      "HIGH": 2,
      "MEDIUM": 2,
      "LOW": 1
    },
    "by_category": {
      "bug": 2,
      "security": 1,
      "best_practice": 2
    }
  }
}
