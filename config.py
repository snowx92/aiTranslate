import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Keys for online services (use environment variables for security)
    HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Legacy cache directory (no longer needed for online APIs)
    # CACHE_DIR = r"C:\Users\hesha\.cache\huggingface\hub"
