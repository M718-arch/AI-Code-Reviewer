#!/bin/bash

# ============================================================================
# AI CODE REVIEWER - Complete Setup Script
# ============================================================================
# Version: 2.0.0 | 41 Analysis Engines | 12 Languages Supported
# Repository: https://github.com/M718-arch/AI-Code-Reviewer
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

print_header() {
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                    AI CODE REVIEWER v2.0.0                       ║"
    echo "║                     41 Engine Edition                            ║"
    echo "║                   12 Languages Supported                         ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    else
        print_success "$1 found: $(command -v $1)"
    fi
}

# ============================================================================
# INITIALIZATION
# ============================================================================

clear
print_header

print_info "Starting AI Code Reviewer setup..."
print_info "This script will install and configure everything you need."
echo ""

# Check prerequisites
print_info "Checking prerequisites..."
check_command git
check_command python3
check_command node
check_command npm
check_command docker 2>/dev/null && print_success "Docker found" || print_warning "Docker not found (optional)"
echo ""

# ============================================================================
# 1. CLONE REPOSITORY
# ============================================================================

print_info "Step 1/8: Cloning repository..."
if [ -d "AI-Code-Reviewer" ]; then
    print_warning "Repository already exists. Updating..."
    cd AI-Code-Reviewer
    git pull
else
    git clone https://github.com/M718-arch/AI-Code-Reviewer.git
    cd AI-Code-Reviewer
fi
print_success "Repository ready"
echo ""

# ============================================================================
# 2. BACKEND SETUP
# ============================================================================

print_info "Step 2/8: Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
black==23.12.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
flake8==6.1.0
mypy==1.7.0
EOF

pip install --upgrade pip
pip install -r requirements.txt
print_success "Backend dependencies installed"
echo ""

# ============================================================================
# 3. FRONTEND SETUP
# ============================================================================

print_info "Step 3/8: Setting up frontend..."
cd ../frontend

# Create package.json
cat > package.json << 'EOF'
{
  "name": "code-reviewer-frontend",
  "version": "2.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "highlight.js": "^11.9.0",
    "react-highlight": "^0.15.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "lint": "eslint src/**/*.{js,jsx}",
    "format": "prettier --write \"src/**/*.{js,jsx,css,md}\""
  },
  "eslintConfig": {
    "extends": ["react-app", "react-app/jest"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "devDependencies": {
    "eslint": "^8.53.0",
    "prettier": "^3.0.0"
  }
}
EOF

npm install
print_success "Frontend dependencies installed"
echo ""

# ============================================================================
# 4. CREATE SAMPLE CODE
# ============================================================================

print_info "Step 4/8: Creating sample code for testing..."

cat > pasted_code.py << 'EOF'
#!/usr/bin/env python3
"""
Sample Calculator Module
Used for testing the AI Code Reviewer
"""

import os
import logging
from typing import Optional, List, Union
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Operation(Enum):
    """Supported mathematical operations"""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@dataclass
class Calculation:
    """Represents a single calculation"""
    operation: Operation
    a: float
    b: float
    result: float


class Calculator:
    """
    A simple calculator class with proper error handling and history tracking.
    
    Features:
    - Basic arithmetic operations
    - Operation history
    - Error handling for edge cases
    - Type hints for better code clarity
    """
    
    def __init__(self, name: str = "Default Calculator") -> None:
        """
        Initialize the calculator.
        
        Args:
            name: Calculator instance name
        """
        self.name = name
        self._history: List[Calculation] = []
        self._last_result: Optional[float] = None
        logger.info(f"Calculator '{name}' initialized")
        
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Add two numbers and store in history."""
        result = float(a + b)
        self._store_calculation(Operation.ADD, a, b, result)
        logger.debug(f"Addition: {a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Subtract b from a and store in history."""
        result = float(a - b)
        self._store_calculation(Operation.SUBTRACT, a, b, result)
        logger.debug(f"Subtraction: {a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Multiply two numbers and store in history."""
        result = float(a * b)
        self._store_calculation(Operation.MULTIPLY, a, b, result)
        logger.debug(f"Multiplication: {a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide a by b with error handling.
        
        Raises:
            ValueError: If attempting to divide by zero
        """
        if b == 0:
            logger.error(f"Division by zero attempted: {a} / {b}")
            raise ValueError("Cannot divide by zero")
        
        result = float(a / b)
        self._store_calculation(Operation.DIVIDE, a, b, result)
        logger.debug(f"Division: {a} / {b} = {result}")
        return result
    
    def _store_calculation(self, op: Operation, a: float, b: float, result: float) -> None:
        """Store calculation in history."""
        calculation = Calculation(operation=op, a=float(a), b=float(b), result=result)
        self._history.append(calculation)
        self._last_result = result
    
    def get_history(self) -> List[Calculation]:
        """Return calculation history."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self._history.clear()
        self._last_result = None
        logger.info("History cleared")
    
    def get_last_result(self) -> Optional[float]:
        """Return the last calculation result."""
        return self._last_result
    
    def __str__(self) -> str:
        """String representation of the calculator."""
        return f"Calculator(name='{self.name}', calculations={len(self._history)})"
    
    def __repr__(self) -> str:
        """Detailed representation of the calculator."""
        return f"Calculator(name='{self.name}', history_length={len(self._history)})"


def main():
    """Example usage of the Calculator class."""
    print("🔢 Calculator Demo")
    print("=" * 50)
    
    # Create calculator instance
    calc = Calculator("Demo Calculator")
    
    # Perform calculations
    print(f"\n📊 Performing calculations:")
    print(f"  5 + 3 = {calc.add(5, 3)}")
    print(f"  10 - 4 = {calc.subtract(10, 4)}")
    print(f"  6 * 7 = {calc.multiply(6, 7)}")
    print(f"  15 / 3 = {calc.divide(15, 3)}")
    
    # Show history
    print(f"\n📜 Calculation History:")
    for i, calc_item in enumerate(calc.get_history(), 1):
        print(f"  {i}. {calc_item.operation.value}: {calc_item.a} {calc_item.b} = {calc_item.result}")
    
    # Test error handling
    print(f"\n⚠️  Testing Error Handling:")
    try:
        calc.divide(10, 0)
    except ValueError as e:
        print(f"  ✓ Caught expected error: {e}")
    
    # Show calculator info
    print(f"\nℹ️  {calc}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
EOF

print_success "Sample code created: pasted_code.py"
echo ""

# ============================================================================
# 5. DOCKER SETUP
# ============================================================================

print_info "Step 5/8: Creating Docker configuration..."

cd ..

# Create .dockerignore
cat > .dockerignore << 'EOF'
node_modules
.git
*.log
*.pyc
__pycache__
.env
.vscode
.idea
.DS_Store
venv
venv/
EOF

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: code-reviewer-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - MAX_FILE_SIZE=10485760
      - LOG_LEVEL=info
    networks:
      - code-reviewer-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: code-reviewer-frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
      - REACT_APP_VERSION=2.0.0
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - code-reviewer-network

networks:
  code-reviewer-network:
    driver: bridge
EOF

# Create Dockerfile.backend
cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

# Create Dockerfile.frontend
cat > Dockerfile.frontend << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY frontend/ .

# Build the app
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
EOF

print_success "Docker configuration created"
echo ""

# ============================================================================
# 6. CREATE ENVIRONMENT FILES
# ============================================================================

print_info "Step 6/8: Creating environment configuration..."

# Backend .env
cat > backend/.env << 'EOF'
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.py,.js,.java,.cpp,.c,.cs,.php,.rb,.go,.rs,.swift,.kt,.ts,.html,.css
LOG_LEVEL=info
ENVIRONMENT=development
EOF

# Frontend .env
cat > frontend/.env << 'EOF'
# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_VERSION=2.0.0
REACT_APP_MAX_FILE_SIZE=10
EOF

print_success "Environment files created"
echo ""

# ============================================================================
# 7. CREATE USEFUL SCRIPTS
# ============================================================================

print_info "Step 7/8: Creating utility scripts..."

# Create start-dev.sh
cat > start-dev.sh << 'EOF'
#!/bin/bash
# Start development environment

echo "🚀 Starting AI Code Reviewer development environment..."

# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm start &
FRONTEND_PID=$!

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x start-dev.sh

# Create test.sh
cat > test.sh << 'EOF'
#!/bin/bash
# Run tests

echo "🧪 Running tests..."

# Backend tests
cd backend
source venv/bin/activate
pytest tests/ -v --cov=. --cov-report=term-missing

# Frontend tests
cd ../frontend
npm test -- --coverage
EOF

chmod +x test.sh

print_success "Utility scripts created"
echo ""

# ============================================================================
# 8. USEFUL ALIASES
# ============================================================================

print_info "Step 8/8: Adding useful aliases to shell configuration..."

# Detect shell
SHELL_CONFIG="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
fi

cat >> "$SHELL_CONFIG" << 'EOF'

# ============================================================================
# AI Code Reviewer Aliases
# ============================================================================

# Navigation
alias cr='cd ~/AI-Code-Reviewer'
alias cr-backend='cd ~/AI-Code-Reviewer/backend && source venv/bin/activate'
alias cr-frontend='cd ~/AI-Code-Reviewer/frontend'

# Development
alias cr-start='cd ~/AI-Code-Reviewer && ./start-dev.sh'
alias cr-docker='cd ~/AI-Code-Reviewer && docker-compose up'
alias cr-docker-down='cd ~/AI-Code-Reviewer && docker-compose down'
alias cr-logs='cd ~/AI-Code-Reviewer && docker-compose logs -f'

# Testing
alias cr-test='cd ~/AI-Code-Reviewer && ./test.sh'
alias cr-lint='cd ~/AI-Code-Reviewer/backend && source venv/bin/activate && flake8 . && black --check .'
alias cr-format='cd ~/AI-Code-Reviewer/backend && source venv/bin/activate && black .'

# API
alias cr-api='curl -X POST http://localhost:8000/api/review -H "Content-Type: application/json" -d'
alias cr-health='curl http://localhost:8000/health'

# Info
alias cr-version='echo "AI Code Reviewer v2.0.0 - 41 Engine Edition | 12 Languages Supported"'
alias cr-status='cd ~/AI-Code-Reviewer && docker-compose ps'
EOF

print_success "Aliases added to $SHELL_CONFIG"
echo ""

# ============================================================================
# COMPLETION
# ============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                    INSTALLATION COMPLETE!                        ║"
echo "╠═══════════════════════════════════════════════════════════════════╣"
echo "║                                                                   ║"
echo "║  📦 AI Code Reviewer v2.0.0                                       ║"
echo "║  🔧 41 Analysis Engines                                           ║"
echo "║  🌐 12 Languages Supported                                        ║"
echo "║                                                                   ║"
echo "║  🚀 Quick Start Commands:                                         ║"
echo "║     ./start-dev.sh     - Start development environment            ║"
echo "║     docker-compose up  - Start with Docker                        ║"
echo "║     ./test.sh          - Run all tests                            ║"
echo "║                                                                   ║"
echo "║  📍 Access Points:                                                ║"
echo "║     Frontend: http://localhost:3000                               ║"
echo "║     Backend API: http://localhost:8000                            ║"
echo "║     API Docs: http://localhost:8000/docs                          ║"
echo "║     Health Check: http://localhost:8000/health                    ║"
echo "║                                                                   ║"
echo "║  📁 Project Structure:                                            ║"
echo "║     ./backend/  - FastAPI backend                                 ║"
echo "║     ./frontend/ - React frontend                                  ║"
echo "║     pasted_code.py - Sample code for testing                      ║"
echo "║                                                                   ║"
echo "║  ⭐ Don't forget to star the repo:                                ║"
echo "║     https://github.com/M718-arch/AI-Code-Reviewer                 ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"

# Source the shell config
print_info "Reloading shell configuration..."
source "$SHELL_CONFIG" 2>/dev/null || true

echo ""
print_success "Setup complete! You can now use 'cr-version' to verify installation."
print_info "Please restart your terminal or run: source $SHELL_CONFIG"
echo ""
