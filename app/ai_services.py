import os
import google.generativeai as genai
import json
from typing import Dict, List
from google.api_core import exceptions

class GeminiAIService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        
        try:
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Test the configuration with a simple prompt
            response = self.model.generate_content("Test")
            if not response:
                raise ValueError("Failed to get response from model")
                
        except exceptions.InvalidArgument:
            raise ValueError("Invalid API key")
        except exceptions.NotFound:
            raise ValueError("Model not found. Please check your API access and model name.")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini AI service: {str(e)}")

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
        
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("Empty response from model")
                
            # Parse the response text as JSON
            word_data = json.loads(response.text)
            
            # Validate required fields
            required_fields = ['word', 'meaning', 'example_sentence', 'rephrased_meaning']
            for field in required_fields:
                if field not in word_data:
                    raise ValueError(f"Missing required field: {field}")
                    
            return word_data
            
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return self._get_fallback_word()
        except Exception as e:
            print(f"Error generating daily word: {str(e)}")
            return self._get_fallback_word()

    def generate_quiz_questions(self, word: str) -> List[Dict]:
        """
        Generate quiz questions for the word of the day
        """
        prompt = f"""
        Create 3 multiple-choice quiz questions about the word '{word}' 
        that test different aspects of understanding. 
        Each question should have 4 options (A, B, C, D) with only one correct answer.
        Format each question as a JSON object with:
        {{
            "question": "The actual question text",
            "options": [
                "Option A - First option",
                "Option B - Second option",
                "Option C - Third option",
                "Option D - Fourth option"
            ],
            "correct_answer": "The correct option (e.g., 'Option A - First option')"
        }}
        
        Make sure the options are meaningful and related to the word's meaning, usage, or context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise ValueError("Empty response from model")
                
            # Parse the response text as JSON
            questions = json.loads(response.text)
            
            # Validate questions format
            if not isinstance(questions, list):
                raise ValueError("Response is not a list of questions")
                
            for question in questions:
                if not all(key in question for key in ['question', 'options', 'correct_answer']):
                    raise ValueError("Invalid question format")
                if len(question['options']) != 4:
                    raise ValueError("Each question must have exactly 4 options")
                    
            return questions
            
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return self._get_fallback_quiz(word)
        except Exception as e:
            print(f"Error generating quiz questions: {str(e)}")
            return self._get_fallback_quiz(word)

    def _get_fallback_word(self) -> Dict:
        """Return a fallback word when API fails"""
        return {
            "word": "Serendipity",
            "meaning": "The occurrence of events by chance in a beneficial way",
            "synonyms": ["luck", "fortune", "chance"],
            "antonyms": ["misfortune", "bad luck"],
            "example_sentence": "Her discovery of the rare book was pure serendipity.",
            "rephrased_meaning": "Finding something wonderful when you weren't specifically looking for it"
        }

    def _get_fallback_quiz(self, word: str) -> List[Dict]:
        """Return a fallback quiz when API fails"""
        return [
            {
                "question": f"What is the meaning of '{word}'?",
                "options": [
                    "The occurrence of events by chance in a beneficial way",
                    "A planned sequence of events",
                    "A random occurrence with no benefit",
                    "A predictable outcome"
                ],
                "correct_answer": "The occurrence of events by chance in a beneficial way"
            },
            {
                "question": f"Which of these is an example of {word}?",
                "options": [
                    "Following a detailed schedule",
                    "Finding a rare book while looking for something else",
                    "Calculating a mathematical equation",
                    "Following a recipe exactly"
                ],
                "correct_answer": "Finding a rare book while looking for something else"
            },
            {
                "question": f"Which word is NOT a synonym of {word}?",
                "options": [
                    "Luck",
                    "Fortune",
                    "Chance",
                    "Planning"
                ],
                "correct_answer": "Planning"
            }
        ]