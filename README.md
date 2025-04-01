# Vocabulary Enhancer Platform

## Features
- AI-powered daily word recommendations
- Personalized quiz generation
- User authentication
- Learning streak tracking
- Comprehensive dashboard

## Prerequisites
- Python 3.8+
- Gemini API Key

## Setup Instructions
1. Clone the repository
2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Set environment variables
   ```
   export GEMINI_API_KEY=your_gemini_api_key
   export SECRET_KEY=your_secret_key
   ```
5. Initialize the database
   ```
   flask db upgrade
   ```
6. Run the application
   ```
   python run.py
   ```

## Environment Configuration
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///vocabulary_enhancer.db
```