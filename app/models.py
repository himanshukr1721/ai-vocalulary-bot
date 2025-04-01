from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    interests = db.Column(db.String(255), nullable=True)
    preferred_difficulty = db.Column(db.String(50), nullable=True)
    learning_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime, nullable=True)
    
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    daily_words = db.relationship('DailyWord', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_learning_streak(self):
        today = datetime.utcnow().date()
        if self.last_activity_date:
            last_date = self.last_activity_date.date()
            if last_date == today - timedelta(days=1):
                self.learning_streak += 1
            elif last_date < today - timedelta(days=1):
                self.learning_streak = 1
        else:
            self.learning_streak = 1
        
        self.last_activity_date = datetime.utcnow()

class DailyWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    synonyms = db.Column(db.Text, nullable=True)
    antonyms = db.Column(db.Text, nullable=True)
    example_sentence = db.Column(db.Text, nullable=True)
    rephrased_meaning = db.Column(db.Text, nullable=True)
    date_learned = db.Column(db.DateTime, default=datetime.utcnow)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    quiz_questions = db.Column(db.Text, nullable=False)
    user_answers = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)