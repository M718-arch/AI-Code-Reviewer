"""
AI Code Reviewer - FastAPI Backend
Run with: uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import analyzer modules
try:
    from code_analyzer import CodeAnalyzer
    from utils import detect_language, count_lines_of_code, extract_functions
    from reviewer_chain import review_chain
    ANALYZER_AVAILABLE = True
    print("✅ Analyzer modules loaded")
except ImportError as e:
    ANALYZER_AVAILABLE = False
    print(f"⚠️ Warning: {e}")
    
    # Fallback classes
    class CodeAnalyzer:
        def __init__(self, language='python'): 
            pass
        
        def analyze(self, code): 
            return []
    
    def detect_language(code, filename=None): 
        return 'python'
    
    def count_lines_of_code(code): 
        return len(code.split('\n')), len(code.split('\n'))
    
    def extract_functions(code, language): 
        return []
    
    class MockChain:
        def generate_summary(self, issues, language):
            return {
                'total_issues': len(issues),
                'by_severity': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'by_category': {},
                'language': language
            }
    
    review_chain = MockChain()

app = FastAPI(title="AI Code Reviewer API")

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = None

class CodeReviewResponse(BaseModel):
    issues: List[Dict[str, Any]]
    summary: Dict[str, Any]
    language: str
    stats: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "AI Code Reviewer API", "status": "online"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "analyzer": ANALYZER_AVAILABLE}

@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    try:
        code = request.code
        filename = request.filename or "code.py"
        
        language = detect_language(code, filename)
        analyzer = CodeAnalyzer(language)
        issues = analyzer.analyze(code)
        
        non_empty, total = count_lines_of_code(code)
        functions = extract_functions(code, language)
        
        summary = review_chain.generate_summary(issues, language)
        
        stats = {
            'total_lines': total,
            'code_lines': non_empty,
            'functions': len(functions),
            'characters': len(code)
        }
        
        return {
            "issues": issues,
            "summary": summary,
            "language": language,
            "stats": stats
        }
    except Exception as e:
        print(f"Error in review_code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        code = content.decode('utf-8')
        return {
            "filename": file.filename,
            "code": code,
            "size": len(code)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 BACKEND RUNNING")
    print("="*50)
    print("\n📍 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    print("\n✅ Press Ctrl+C to stop\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)