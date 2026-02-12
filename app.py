"""
AI Code Reviewer - COMPLETELY FIXED VERSION
All indentation errors and f-string bugs fixed
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import traceback
import importlib.util

# ============================================================================
# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
# ============================================================================
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CHECK AND LOAD DEPENDENCIES WITH FALLBACKS
# ============================================================================

# Try to import config, provide defaults if fails
try:
    from config import APP_TITLE, APP_ICON, APP_LAYOUT, SEVERITY_LEVELS
except ImportError:
    APP_TITLE = "🤖 AI Code Reviewer"
    APP_ICON = "🤖"
    APP_LAYOUT = "wide"
    SEVERITY_LEVELS = {
        "HIGH": "🔴 High",
        "MEDIUM": "🟡 Medium",
        "LOW": "🟢 Low"
    }
    st.warning("⚠️ Config file not found, using defaults")

# Try to import utils with fallbacks
try:
    from utils import (
        detect_language, validate_file_size, validate_file_extension,
        format_code, count_lines_of_code, extract_functions
    )
    UTILS_AVAILABLE = True
except ImportError as e:
    UTILS_AVAILABLE = False
    st.warning(f"⚠️ Utils module not loaded: {str(e)}")
    
    # Provide fallback functions
    def detect_language(code, filename=None): 
        return 'python'
    def validate_file_size(file): 
        return True, "OK"
    def validate_file_extension(filename): 
        return True, "OK"
    def format_code(code, language): 
        return code
    def count_lines_of_code(code): 
        lines = code.split('\n')
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        return len(non_empty), len(lines)
    def extract_functions(code, language): 
        return []

# Try to import code_analyzer
try:
    from code_analyzer import CodeAnalyzer, run_pylint
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    class CodeAnalyzer:
        def __init__(self, language): 
            pass
        def analyze(self, code): 
            return []
    def run_pylint(code): 
        return []

# Try to import HF models
try:
    from hf_models import get_code_review_ai
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    def get_code_review_ai(): 
        return None

# Try to import reviewer_chain
try:
    from reviewer_chain import review_chain
    CHAIN_AVAILABLE = True
except ImportError:
    CHAIN_AVAILABLE = False
    class MockReviewChain:
        def combine_issues(self, static, ai): 
            return static
        def generate_summary(self, issues, language): 
            return {
                'total_issues': len(issues),
                'by_severity': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
                'by_category': {},
                'language': language
            }
        def suggest_fix(self, code, issue): 
            return "Manual fix required"
    review_chain = MockReviewChain()

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================
if 'review_history' not in st.session_state:
    st.session_state.review_history = []
if 'current_review' not in st.session_state:
    st.session_state.current_review = None
if 'app_initialized' not in st.session_state:
    st.session_state.app_initialized = True

# ============================================================================
# CUSTOM CSS - SAFE VERSION
# ============================================================================
st.markdown("""
<style>
    /* Main styles */
    .main-header {
        font-size: 2.5rem;
        color: #FF4B4B;
        text-align: center;
        padding: 1rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #FF4B4B;
    }
    
    /* Issue cards */
    .issue-high {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #d32f2f;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .issue-medium {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #f57c00;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .issue-low {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.5rem solid #388e3c;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card label {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
    }
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    
    /* Sidebar */
    .sidebar-content {
        padding: 1rem;
    }
    
    /* Status messages */
    .stAlert {
        border-radius: 0.5rem;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def show_error_ui(error_message):
    """Show error UI with graceful degradation"""
    st.error(f"⚠️ {error_message}")
    st.markdown("""
    ### 🔧 Quick Fix:
    1. Make sure all dependencies are installed:
       ```bash
       pip install -r requirements.txt
       ```
    2. Check that all project files are present:
       - `utils.py`
       - `config.py` 
       - `code_analyzer.py`
       - `hf_models.py`
       - `reviewer_chain.py`
    
    3. Restart the app:
       ```bash
       streamlit run app.py
       ```
    """)
    
    with st.expander("🐛 Detailed Error Info"):
        st.code(error_message)
        st.info(f"Python version: {sys.version}")
        st.info(f"Streamlit version: {st.__version__}")

def main():
    """Main application function"""
    
    try:
        # ====================================================================
        # SIDEBAR
        # ====================================================================
        with st.sidebar:
            # Logo and title
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image("https://img.icons8.com/fluency/96/null/robot.png", width=60)
            with col2:
                st.title("AI Code Reviewer")
            
            st.markdown("---")
            
            # Status indicators
            st.subheader("🔧 System Status")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("✅ App")
            with col2:
                status = "✅" if UTILS_AVAILABLE else "❌"
                st.markdown(status, unsafe_allow_html=True)
            
            with col1:
                st.markdown("🤖 AI")
            with col2:
                status = "✅" if HF_AVAILABLE else "⚠️"
                st.markdown(status, unsafe_allow_html=True)
            
            with col1:
                st.markdown("📊 Analyzer")
            with col2:
                status = "✅" if ANALYZER_AVAILABLE else "⚠️"
                st.markdown(status, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Supported languages
            st.subheader("📋 Supported Languages")
            languages = [
                "🐍 Python", "📘 JavaScript", "☕ Java", 
                "⚙️ C++", "💠 C#", "🐘 PHP", "💎 Ruby",
                "🔷 Go", "🦀 Rust", "📱 Swift", "🎯 Kotlin",
                "📝 TypeScript", "🌐 HTML", "🎨 CSS"
            ]
            for lang in languages[:7]:
                st.markdown(f"- {lang}")
            
            with st.expander("Show more..."):
                for lang in languages[7:]:
                    st.markdown(f"- {lang}")
            
            st.markdown("---")
            
            # Stats
            st.subheader("📊 Statistics")
            if st.session_state.review_history:
                st.metric(
                    "Total Reviews",
                    len(st.session_state.review_history),
                    delta="Today"
                )
                
                total_issues = sum(
                    r.get('summary', {}).get('total_issues', 0) 
                    for r in st.session_state.review_history
                )
                if len(st.session_state.review_history) > 0:
                    avg_issues = total_issues / len(st.session_state.review_history)
                    st.metric("Avg Issues/Review", f"{avg_issues:.1f}")
            else:
                st.info("No reviews yet")
            
            st.markdown("---")
            
            # Settings
            st.subheader("⚙️ Settings")
            use_ai = st.checkbox("🤖 Enable AI Review", value=HF_AVAILABLE)
            use_static = st.checkbox("🔍 Static Analysis", value=True)
            auto_format = st.checkbox("✨ Auto-format code", value=False)
            show_preview = st.checkbox("📄 Show code preview", value=True)
            
            st.markdown("---")
            
            # About
            with st.expander("🚀 About"):
                st.markdown("""
                **AI Code Reviewer** helps you:
                - 🐛 Find bugs and errors
                - ⚡ Improve performance
                - 🔒 Detect security issues
                - 📝 Enhance code style
                
                **Version:** 1.0.0
                **Engine:** CodeBERT/CodeLlama
                """)
        
        # ====================================================================
        # MAIN CONTENT
        # ====================================================================
        
        # Header
        st.markdown('<h1 class="main-header">🤖 AI Code Reviewer</h1>', unsafe_allow_html=True)
        
        # Welcome message
        if not st.session_state.review_history:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 1rem; color: white; margin-bottom: 2rem;">
                <h2 style="color: white; margin-top: 0;">👋 Welcome to AI Code Reviewer!</h2>
                <p style="font-size: 1.1rem;">
                    Upload your code and get instant AI-powered feedback on bugs, 
                    performance issues, and best practices.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Input methods
        st.subheader("📤 Choose Input Method")
        input_method = st.radio(
            "Select input method:",
            ["📁 Upload File", "📝 Paste Code", "🔗 GitHub URL"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        code = ""
        filename = None
        
        # ====================================================================
        # FILE UPLOAD HANDLER
        # ====================================================================
        if input_method == "📁 Upload File":
            uploaded_file = st.file_uploader(
                "Drop your code file here",
                type=['py', 'js', 'java', 'cpp', 'c', 'cs', 'php', 'rb', 
                      'go', 'rs', 'swift', 'kt', 'ts', 'html', 'css'],
                help="Maximum file size: 10MB"
            )
            
            if uploaded_file:
                try:
                    is_valid_size, size_msg = validate_file_size(uploaded_file)
                    is_valid_ext, ext_msg = validate_file_extension(uploaded_file.name)
                    
                    if not is_valid_size:
                        st.error(f"❌ {size_msg}")
                    elif not is_valid_ext:
                        st.error(f"❌ {ext_msg}")
                    else:
                        code = uploaded_file.read().decode("utf-8")
                        filename = uploaded_file.name
                        st.success(f"✅ Successfully loaded: {filename}")
                        
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        # ====================================================================
        # PASTE CODE HANDLER
        # ====================================================================
        elif input_method == "📝 Paste Code":
            code = st.text_area(
                "Paste your code here:",
                height=300,
                placeholder="# Write or paste your code here...\n\ndef hello():\n    print('Hello, World!')",
                help="Paste your code and optionally give it a filename"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                filename = st.text_input("Filename (optional)", "pasted_code.py")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📋 Clear", use_container_width=True):
                    st.rerun()
        
        # ====================================================================
        # GITHUB URL HANDLER
        # ====================================================================
        else:
            github_url = st.text_input(
                "Enter GitHub raw URL:",
                placeholder="https://raw.githubusercontent.com/username/repo/main/file.py",
                help="Paste the raw URL of a GitHub file"
            )
            
            if github_url:
                try:
                    import requests
                    with st.spinner("Fetching code from GitHub..."):
                        response = requests.get(github_url, timeout=10)
                        
                    if response.status_code == 200:
                        code = response.text
                        filename = github_url.split('/')[-1]
                        st.success(f"✅ Successfully fetched: {filename}")
                        
                        with st.expander("📄 Fetched Code Preview", expanded=False):
                            preview = code[:500] + "..." if len(code) > 500 else code
                            st.code(preview, language='python')
                    else:
                        st.error(f"❌ Failed to fetch code. Status code: {response.status_code}")
                        
                except ImportError:
                    st.error("❌ Requests library not installed. Run: pip install requests")
                except Exception as e:
                    st.error(f"❌ Error fetching URL: {str(e)}")
        
        # ====================================================================
        # CODE ANALYSIS SECTION - FIXED VERSION (NO F-STRING BACKSLASHES)
        # ====================================================================
        if code.strip():
            st.markdown("---")
            
            # Language detection
            language = detect_language(code, filename)
            
            # Language badge colors
            lang_colors = {
                'python': '#3776AB', 'javascript': '#F7DF1E', 'java': '#007396',
                'cpp': '#00599C', 'csharp': '#239120', 'php': '#777BB4',
                'ruby': '#CC342D', 'go': '#00ADD8', 'rust': '#000000'
            }
            lang_color = lang_colors.get(language.lower(), '#6B7280')
            
            # Calculate values OUTSIDE the f-string (THIS FIXES THE BACKSLASH ERROR!)
            line_count = len(code.split('\n'))
            char_count = len(code)
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="background-color: {lang_color}; color: white; 
                           padding: 0.25rem 1rem; border-radius: 2rem; font-weight: 600;">
                    {language.upper()}
                </span>
                <span style="color: #6B7280;">
                    {line_count} lines • {char_count} characters
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Code preview
            if show_preview:
                with st.expander("📄 Code Preview", expanded=False):
                    if auto_format and UTILS_AVAILABLE:
                        formatted_code = format_code(code, language)
                    else:
                        formatted_code = code
                    st.code(formatted_code, language=language)
            
            # Code statistics
            st.subheader("📊 Code Statistics")
            non_empty_lines, total_lines = count_lines_of_code(code)
            functions = extract_functions(code, language)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📏 Total Lines", 
                    total_lines,
                    help="Total number of lines in the file"
                )
            with col2:
                st.metric(
                    "📝 Code Lines", 
                    non_empty_lines,
                    help="Non-empty, non-comment lines",
                    delta=f"{total_lines - non_empty_lines} comments"
                )
            with col3:
                st.metric(
                    "🔧 Functions", 
                    len(functions),
                    help="Number of functions/methods detected"
                )
            with col4:
                if len(functions) > 10:
                    complexity = "High"
                elif len(functions) > 5:
                    complexity = "Medium"
                else:
                    complexity = "Low"
                st.metric(
                    "📊 Complexity", 
                    complexity,
                    help="Based on number of functions"
                )
            
            # Review button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                button_text = "🚀 START CODE REVIEW" if not st.session_state.current_review else "🔄 REVIEW AGAIN"
                review_button = st.button(
                    button_text,
                    type="primary",
                    use_container_width=True
                )
            
            # ================================================================
            # PERFORM CODE REVIEW
            # ================================================================
            if review_button:
                with st.spinner("🔄 Analyzing your code... This may take a moment."):
                    
                    all_issues = []
                    ai_response = ""
                    summary = None
                    
                    try:
                        # 1. Static Analysis
                        if use_static and ANALYZER_AVAILABLE:
                            analyzer = CodeAnalyzer(language)
                            static_issues = analyzer.analyze(code)
                            
                            if language == 'python':
                                try:
                                    pylint_issues = run_pylint(code)
                                    static_issues.extend(pylint_issues)
                                except Exception as e:
                                    st.warning(f"⚠️ Pylint analysis failed: {str(e)}")
                            
                            all_issues.extend(static_issues)
                        
                        # 2. AI Analysis
                        if use_ai and HF_AVAILABLE:
                            try:
                                ai_reviewer = get_code_review_ai()
                                if ai_reviewer:
                                    ai_response = ai_reviewer.review_code(code, language)
                            except Exception as e:
                                ai_response = f"AI analysis unavailable: {str(e)}"
                        
                        # 3. Combine issues
                        if CHAIN_AVAILABLE:
                            all_issues = review_chain.combine_issues(all_issues, ai_response)
                            summary = review_chain.generate_summary(all_issues, language)
                        else:
                            summary = {
                                'total_issues': len(all_issues),
                                'by_severity': {
                                    'HIGH': len([i for i in all_issues if i.get('severity') == 'HIGH']),
                                    'MEDIUM': len([i for i in all_issues if i.get('severity') == 'MEDIUM']),
                                    'LOW': len([i for i in all_issues if i.get('severity') == 'LOW'])
                                },
                                'by_category': {},
                                'language': language
                            }
                            
                            for issue in all_issues:
                                cat = issue.get('category', 'other')
                                summary['by_category'][cat] = summary['by_category'].get(cat, 0) + 1
                        
                        # Save to session state
                        st.session_state.current_review = {
                            'timestamp': datetime.now(),
                            'filename': filename or 'pasted_code',
                            'language': language,
                            'code': code[:1000] + "..." if len(code) > 1000 else code,
                            'issues': all_issues,
                            'summary': summary,
                            'ai_response': ai_response
                        }
                        
                        st.session_state.review_history.append(st.session_state.current_review)
                        st.success("✅ Review completed!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during code review: {str(e)}")
                        with st.expander("🔧 Debug Information"):
                            st.code(traceback.format_exc())
        
        # ====================================================================
        # DISPLAY REVIEW RESULTS
        # ====================================================================
        if st.session_state.current_review:
            review = st.session_state.current_review
            
            st.markdown("---")
            st.markdown("## 📋 Review Results")
            
            # Summary metrics in cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <label>🐛 Total Issues</label>
                    <div class="metric-value">{review['summary']['total_issues']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);">
                    <label>🔴 High Severity</label>
                    <div class="metric-value">{review['summary']['by_severity']['HIGH']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);">
                    <label>🟡 Medium Severity</label>
                    <div class="metric-value">{review['summary']['by_severity']['MEDIUM']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);">
                    <label>🟢 Low Severity</label>
                    <div class="metric-value">{review['summary']['by_severity']['LOW']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Issues by category chart
            if review['summary'].get('by_category'):
                st.subheader("📊 Issues by Category")
                
                cat_data = {
                    'Category': list(review['summary']['by_category'].keys()),
                    'Count': list(review['summary']['by_category'].values())
                }
                cat_df = pd.DataFrame(cat_data)
                if not cat_df.empty:
                    cat_df = cat_df.sort_values('Count', ascending=True)
                    st.bar_chart(cat_df.set_index('Category'))
            
            # Detailed issues
            st.subheader("🔍 Detailed Issues")
            
            if not review['issues']:
                st.success("""
                ### 🎉 Perfect code! No issues found!
                
                Your code follows best practices and has no detectable issues.
                """)
            else:
                for i, issue in enumerate(review['issues']):
                    severity = issue.get('severity', 'LOW').upper()
                    
                    if severity == 'HIGH':
                        css_class = 'issue-high'
                        severity_text = '🔴 HIGH'
                    elif severity == 'MEDIUM':
                        css_class = 'issue-medium'
                        severity_text = '🟡 MEDIUM'
                    else:
                        css_class = 'issue-low'
                        severity_text = '🟢 LOW'
                    
                    with st.container():
                        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            st.markdown(f"### 📍")
                        with col2:
                            st.markdown(f"**Line {issue.get('line', '?')}** • {severity_text}")
                        
                        st.markdown(f"**Issue:** {issue.get('problem', 'Unknown issue')}")
                        st.markdown(f"**💡 Suggestion:** {issue.get('suggestion', 'No suggestion available')}")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            if issue.get('category'):
                                st.markdown(f"**Category:** `{issue.get('category')}`")
                        with col2:
                            button_key = f"fix_{i}_{issue.get('line', 0)}"
                            if st.button("🔧 Show Fix", key=button_key, use_container_width=True):
                                try:
                                    if CHAIN_AVAILABLE:
                                        fix = review_chain.suggest_fix(review['code'], issue)
                                    else:
                                        fix = "# Suggested fix:\n"
                                        if 'bare except' in issue.get('problem', '').lower():
                                            fix = "except Exception as e:"
                                        elif 'None' in issue.get('problem', ''):
                                            fix = "if x is None:"
                                        else:
                                            fix = "# Manual review required"
                                    
                                    st.code(fix, language=review['language'])
                                except Exception as e:
                                    st.error(f"Could not generate fix: {str(e)}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # AI Response
            if review.get('ai_response') and review['ai_response'] not in ["AI model not loaded", "", None]:
                with st.expander("🤖 AI Analysis Details", expanded=False):
                    st.markdown("### 🤖 AI Code Review")
                    st.markdown(review['ai_response'])
            
            # Export options
            st.subheader("📤 Export Results")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                report = f"""AI CODE REVIEW REPORT
{'='*50}
File: {review['filename']}
Language: {review['language']}
Date: {review['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
{'-'*20}
Total Issues: {review['summary']['total_issues']}
  • High: {review['summary']['by_severity']['HIGH']}
  • Medium: {review['summary']['by_severity']['MEDIUM']}
  • Low: {review['summary']['by_severity']['LOW']}

DETAILED ISSUES
{'-'*20}
"""
                for issue in review['issues']:
                    report += f"""
Line {issue.get('line', '?')}: {issue.get('problem', 'Unknown')}
  Severity: {issue.get('severity', 'LOW')}
  Suggestion: {issue.get('suggestion', 'N/A')}
  Category: {issue.get('category', 'other')}
{'-'*40}
"""
                
                st.download_button(
                    "📥 Download Report (TXT)",
                    report,
                    file_name=f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    use_container_width=True
                )
            
            with col2:
                try:
                    import json
                    review_json = json.dumps(review, default=str, indent=2)
                    st.download_button(
                        "📊 Download Report (JSON)",
                        review_json,
                        file_name=f"code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        use_container_width=True
                    )
                except Exception:
                    st.button("📊 JSON Export Unavailable", disabled=True, use_container_width=True)
            
            with col3:
                if st.button("🔄 New Review", use_container_width=True):
                    st.session_state.current_review = None
                    st.rerun()
        
        # ====================================================================
        # REVIEW HISTORY
        # ====================================================================
        if st.session_state.review_history and len(st.session_state.review_history) > 0:
            with st.expander("📜 Review History", expanded=False):
                for i, past_review in enumerate(reversed(st.session_state.review_history[-10:]), 1):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{past_review.get('filename', 'Unknown')}**")
                        timestamp = past_review.get('timestamp', datetime.now())
                        st.caption(f"📅 {timestamp.strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        issues = past_review.get('summary', {}).get('total_issues', 0)
                        st.markdown(f"🐛 {issues} issues")
                    with col3:
                        if st.button("📋 Load", key=f"load_{i}"):
                            st.session_state.current_review = past_review
                            st.rerun()
                    st.markdown("---")
    
    except Exception as e:
        st.error("🚨 An unexpected error occurred!")
        show_error_ui(traceback.format_exc())

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("❌ Critical error in main application")
        st.code(traceback.format_exc())
        st.markdown("""
        ### 🔧 Quick Recovery:
        1. Press `Ctrl+C` in terminal to stop the app
        2. Run: `streamlit run app.py --server.runOnSave=False`
        3. If still failing, try: `pip install --upgrade streamlit`
        """)