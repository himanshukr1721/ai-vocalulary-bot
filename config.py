import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vocabulary_enhancer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set in environment variables")
    
    # Login Configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Application Settings
    DEFAULT_WORD_DIFFICULTY = 'intermediate'
    DEFAULT_USER_INTERESTS = 'general knowledge'

    # Security Settings
    SESSION_COOKIE_SECURE = True
    CSRF_ENABLED = True