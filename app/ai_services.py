import os
import google.generativeai as genai
import json
from typing import Dict, List

class GeminiAIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_daily_word(self, user_interests: str, difficulty: str) -> Dict:
        """
        Generate a personalized word of the day based on user's interests and difficulty level
        """
        prompt = f"""
        Generate a unique English word that would be interesting for someone 
        interested in {user_interests} at a {difficulty} difficulty level. 
        Provide the following details in a JSON format:
        {{
            "word": "",
            "meaning": "",
            "synonyms": [],
            "antonyms": [],
            "example_sentence": "",
            "rephrased_meaning": ""
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback word generation
            return {
                "word": "Serendipity",
                "meaning": "The occurrence of events by chance in a beneficial way",
                "synonyms": ["luck", "fortune", "chance"],
                "antonyms": ["misfortune", "bad luck"],
                "example_sentence": "Her discovery of the rare book was pure serendipity.",
                "rephrased_meaning": "Finding something wonderful when you weren't specifically looking for it"
            }

    def generate_quiz_questions(self, word: str) -> List[Dict]:
        """
        Generate quiz questions for the word of the day
        """
        prompt = f"""
        Create 3 multiple-choice quiz questions about the word '{word}' 
        that test different aspects of understanding. 
        Format each question as a JSON object with:
        {{
            "question": "",
            "options": [],
            "correct_answer": ""
        }}
        """
        
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback quiz questions
            return [
                {
                    "question": f"What is the meaning of '{word}'?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option B"
                }
            ]