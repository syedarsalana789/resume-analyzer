import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # File upload settings
    MAX_ZIP_SIZE_MB: int = int(os.getenv("MAX_ZIP_SIZE_MB", "50"))
    MAX_ZIP_SIZE_BYTES: int = MAX_ZIP_SIZE_MB * 1024 * 1024
    
    # OpenAI settings (optional)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Allowed file extensions
    ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}
    
    # Temporary directory for file processing
    TEMP_DIR = Path("temp_uploads")
    
    @classmethod
    def ensure_temp_dir(cls):
        """Ensure temporary directory exists"""
        cls.TEMP_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def is_llm_enabled(cls) -> bool:
        """Check if LLM extraction is enabled"""
        return bool(cls.OPENAI_API_KEY.strip())

# Initialize configuration
config = Config()
config.ensure_temp_dir()