import os
from dotenv import load_dotenv

load_dotenv()

# Hugging Face settings
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HUGGINGFACE_MODEL = "microsoft/codebert-base"  # أو "codellama/CodeLlama-7b-hf"

# Streamlit settings
APP_TITLE = "🤖 AI Code Reviewer"
APP_ICON = "🤖"
APP_LAYOUT = "wide"

# File settings
ALLOWED_EXTENSIONS = ['.py', '.js', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.html', '.css']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Severity levels
SEVERITY_LEVELS = {
    "HIGH": "🔴 High",
    "MEDIUM": "🟡 Medium", 
    "LOW": "🟢 Low"
}