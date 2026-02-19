#!/bin/bash

# ============================================================================
# AI CODE REVIEWER - Complete Setup & Usage Guide
# ============================================================================
# Welcome to code_reviewer v2.0.0
# 41 Engine Edition | 12 Languages Supported
# ============================================================================

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    AI CODE REVIEWER v2.0.0                       ║"
echo "║                     41 Engine Edition                            ║"
echo "║                   12 Languages Supported                         ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 1. CLONE REPOSITORY
# ============================================================================
echo "📦 Cloning repository..."
git clone https://github.com/M718-arch/AI-Code-Reviewer.git
cd AI-Code-Reviewer

# ============================================================================
# 2. BACKEND SETUP
# ============================================================================
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
black==23.12.0
python-multipart==0.0.6
pydantic==2.5.0
pytest==7.4.3
flake8==6.1.0
EOF

pip install -r requirements.txt

# ============================================================================
# 3. FRONTEND SETUP
# ============================================================================
echo ""
echo "🎨 Setting up frontend..."
cd ../frontend

cat > package.json << 'EOF'
{
  "name": "code-reviewer-frontend",
  "version": "2.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "lint": "eslint src/**/*.js"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  }
}
EOF

npm install

# ============================================================================
# 4. SAMPLE CODE FOR TESTING
# ============================================================================
echo ""
echo "📝 Creating sample code for testing..."

cat > pasted_code.py << 'EOF'
import os
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Calculator:
    """A simple calculator class with proper error handling."""
    
    def __init__(self) -> None:
        """Initialize the calculator."""
        self.__history: List[int] = []
        
    def add(self, a: int, b: int) -> int:
        """Add two numbers and store in history."""
        result = a + b
        self.__history.append(result)
        logger.info(f"Added {a} + {b} = {result}")
        return result
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a and store in history."""
        result = a - b
        self.__history.append(result)
        logger.info(f"Subtracted {a} - {b} = {result}")
        return result
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers and store in history."""
        result = a * b
        self.__history.append(result)
        return result
    
    def divide(self, a: int, b: int) -> float:
        """Divide a by b with error handling."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.__history.append(result)
        return result
    
    def get_history(self) -> List[int]:
        """Return calculation history."""
        return self.__history
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.__history.clear()
        logger.info("History cleared")

# Example usage
if __name__ == "__main__":
    calc = Calculator()
    print("🔢 Calculator Demo")
    print("-" * 30)
    print(f"5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"6 * 7 = {calc.multiply(6, 7)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    print(f"History: {calc.get_history()}")
    
    # Test error handling
    try:
        calc.divide(10, 0)
    except ValueError as e:
        print(f"Error: {e}")
EOF

# ============================================================================
# 5. RUN ANALYSIS
# ============================================================================
echo ""
echo "🔍 Running analysis on sample code..."
echo ""

# Using curl to test the API
echo "📡 Testing API endpoint..."
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nimport logging\nfrom typing import Optional, List\n\nclass Calculator:\n    def __init__(self) -> None:\n        self.__history: List[int] = []\n    \n    def add(self, a: int, b: int) -> int:\n        result = a + b\n        self.__history.append(result)\n        return result\n    \n    def divide(self, a: int, b: int) -> float:\n        if b == 0:\n            raise ValueError(\"Cannot divide by zero\")\n        return a / b",
    "filename": "pasted_code.py"
  }' 2>/dev/null | python -m json.tool || echo "⚠️  API not running. Start with: uvicorn main:app --reload --port 8000"

# ============================================================================
# 6. DOCKER SETUP (Optional)
# ============================================================================
echo ""
echo "🐳 Creating Docker configuration..."

cd ..

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - MAX_FILE_SIZE=10485760

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
EOF

cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

CMD ["npm", "start"]
EOF

# ============================================================================
# 7. USEFUL ALIASES
# ============================================================================
echo ""
echo "⚙️  Adding useful aliases to ~/.bashrc..."

cat >> ~/.bashrc << 'EOF'

# ============================================================================
# AI Code Reviewer Aliases
# ============================================================================
alias cr-backend='cd ~/AI-Code-Reviewer/backend && source venv/bin/activate'
alias cr-frontend='cd ~/AI-Code-Reviewer/frontend && npm start'
alias cr-start='cd ~/AI-Code-Reviewer && docker-compose up'
alias cr-stop='cd ~/AI-Code-Reviewer && docker-compose down'
alias cr-test='cd ~/AI-Code-Reviewer/backend && pytest tests/ -v'
alias cr-lint='cd ~/AI-Code-Reviewer/backend && black . --check && flake8 .'
alias cr-logs='docker-compose logs -f'
alias cr-shell='docker-compose exec backend python'
alias cr-api='curl http://localhost:8000/api/review'
alias cr-version='echo "AI Code Reviewer v2.0.0 - 41 Engine Edition"'
EOF

# ============================================================================
# 8. README CREATION
# ============================================================================
echo ""
echo "📖 Creating README.md..."

cat > README.md << 'EOF'
# AI Code Reviewer 🔍 v2.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.x-61dafb.svg)](https://reactjs.org/)

## 🚀 Quick Start

```bash
# Clone and run
git clone https://github.com/M718-arch/AI-Code-Reviewer.git
cd AI-Code-Reviewer
docker-compose up
