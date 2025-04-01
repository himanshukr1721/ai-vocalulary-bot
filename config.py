import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-secret-key'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vocabulary_enhancer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Login Configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    # Application Settings
    DEFAULT_WORD_DIFFICULTY = 'intermediate'
    DEFAULT_USER_INTERESTS = 'general knowledge'

    # Security Settings
    SESSION_COOKIE_SECURE = True
    CSRF_ENABLED = True