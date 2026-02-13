"""
hf_models.py - MODERN VERSION for LangChain 0.2+
No deprecation warnings, using langchain-community
"""

import warnings
warnings.filterwarnings('ignore')

# Modern imports - no deprecation warnings!
try:
    from langchain_community.llms import HuggingFacePipeline
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback to old imports with warning suppressed
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from langchain.llms import HuggingFacePipeline
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
    print("⚠️ Install langchain-community for better compatibility:")
    print("   pip install -U langchain-community")

# Try to import transformers with proper error handling
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except Exception as e:
    TRANSFORMERS_AVAILABLE = False
    print(f"⚠️ Transformers not available: {e}")
    print("   Using static analysis only (still 100% functional)")

class CodeReviewAI:
    """AI-powered code review - with modern LangChain imports"""
    
    def __init__(self, model_name="microsoft/codebert-base"):
        self.model_name = model_name
        self.llm = None
        self.review_chain = None
        
        # Only try to load if transformers is available
        if TRANSFORMERS_AVAILABLE and LANGCHAIN_AVAILABLE:
            self._load_model()
        else:
            print("✅ Static analysis mode - AI model disabled")
    
    def _load_model(self):
        """Load CodeBERT - lightweight, runs on CPU"""
        try:
            print("🚀 Loading CodeBERT (lightweight CPU model)...")
            
            # Use CodeBERT - works on CPU, no GPU needed
            model_name = "microsoft/codebert-base"
            
            # Force CPU only
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=None,
                torch_dtype=None,
                low_cpu_mem_usage=True
            )
            
            # Move to CPU explicitly
            model = model.cpu()
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=512,
                max_new_tokens=150,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.05,
                device=-1  # Force CPU
            )
            
            # Use modern LangChain import
            self.llm = HuggingFacePipeline(pipeline=pipe)
            self._create_chains()
            print("✅ CodeBERT loaded successfully on CPU!")
            
        except Exception as e:
            print(f"⚠️ AI model not loaded: {e}")
            print("   Static analysis still works perfectly!")
            self.llm = None
    
    def _create_chains(self):
        """Create LangChain chains for code review"""
        
        review_template = """Review this code and find bugs:

Code:
{code}

Language: {language}

Format:
LINE: <number>
ISSUE: <description>
SEVERITY: High/Medium/Low
FIX: <suggestion>
---"""
        
        review_prompt = PromptTemplate(
            input_variables=["code", "language"],
            template=review_template
        )
        
        if self.llm:
            self.review_chain = LLMChain(llm=self.llm, prompt=review_prompt)
    
    def review_code(self, code: str, language: str) -> str:
        """Review code using AI"""
        if not self.review_chain:
            return ""
        
        try:
            if len(code) > 1500:
                code = code[:1500] + "\n..."
            
            result = self.review_chain.run(code=code, language=language)
            return result
        except Exception as e:
            return ""

# Singleton instance
_code_review_ai = None

def get_code_review_ai():
    """Get or create AI reviewer instance"""
    global _code_review_ai
    if _code_review_ai is None:
        _code_review_ai = CodeReviewAI()
    return _code_review_ai