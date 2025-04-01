from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, DailyWord, QuizAttempt
from app import login_manager
from app.ai_services import GeminiAIService
from config import Config
import json
from datetime import datetime
from app import db
# Create blueprint
bp = Blueprint('main', __name__)

# Initialize AI service
ai_service = None

def get_ai_service():
    """Get or create AI service instance"""
    global ai_service
    if ai_service is None:
        try:
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set in environment variables")
            ai_service = GeminiAIService(Config.GEMINI_API_KEY)
        except Exception as e:
            print(f"Error initializing AI service: {str(e)}")
            flash(f"Error initializing AI service: {str(e)}", "error")
            return None
    return ai_service

@bp.before_app_request
def before_first_request():
    """Initialize services when the app starts"""
    try:
        get_ai_service()
    except Exception as e:
        print(f"Error in before_first_request: {str(e)}")
        # Don't flash here as it might be too early in the request cycle

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/')
def index():
    return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('main.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Create a new user and set the password
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        # Save the user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Signup successful! Please log in.')
        return redirect(url_for('main.login'))
    
    return render_template('signup.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Retrieve the user from the database
        user = User.query.filter_by(username=username).first()
        
        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get AI service
    ai_service = get_ai_service()
    if not ai_service:
        flash("AI service is currently unavailable. Please try again later.", "error")
        return render_template('dashboard.html', 
                             word_data=None,
                             quiz_questions=None,
                             previous_words=[],
                             quiz_history=[],
                             learning_streak=current_user.learning_streak,
                             current_quiz_completed=False,
                             quiz_score=None)

    # Check if the user already has a word for today
    today = datetime.utcnow().date()
    daily_word = DailyWord.query.filter(
        DailyWord.user_id == current_user.id, 
        db.func.date(DailyWord.date_learned) == today
    ).first()
    
    # If no word for today, generate a new one
    if not daily_word:
        try:
            # Get user's daily word
            word_data = ai_service.generate_daily_word(
                current_user.interests or Config.DEFAULT_USER_INTERESTS, 
                current_user.preferred_difficulty or Config.DEFAULT_WORD_DIFFICULTY
            )
            
            # Generate quiz questions
            quiz_questions = ai_service.generate_quiz_questions(word_data['word'])
            
            # Save daily word to database
            daily_word = DailyWord(
                user_id=current_user.id,
                word=word_data['word'],
                meaning=word_data['meaning'],
                synonyms=', '.join(word_data.get('synonyms', [])),
                antonyms=', '.join(word_data.get('antonyms', [])),
                example_sentence=word_data['example_sentence'],
                rephrased_meaning=word_data['rephrased_meaning']
            )
            db.session.add(daily_word)
            
            # Save quiz attempt to database
            quiz_attempt = QuizAttempt(
                user_id=current_user.id,
                word=word_data['word'],
                quiz_questions=json.dumps(quiz_questions)
            )
            db.session.add(quiz_attempt)
            
            db.session.commit()
        except Exception as e:
            flash(f"Error generating daily word: {str(e)}", "error")
            return render_template('dashboard.html', 
                                 word_data=None,
                                 quiz_questions=None,
                                 previous_words=[],
                                 quiz_history=[],
                                 learning_streak=current_user.learning_streak,
                                 current_quiz_completed=False,
                                 quiz_score=None)
    else:
        # Convert to dictionary format for template
        word_data = {
            'word': daily_word.word,
            'meaning': daily_word.meaning,
            'synonyms': daily_word.synonyms.split(', ') if daily_word.synonyms else [],
            'antonyms': daily_word.antonyms.split(', ') if daily_word.antonyms else [],
            'example_sentence': daily_word.example_sentence,
            'rephrased_meaning': daily_word.rephrased_meaning
        }
        
        # Get the quiz questions for today's word
        quiz_attempt = QuizAttempt.query.filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.word == daily_word.word,
            db.func.date(QuizAttempt.date_attempted) == today
        ).first()
        
        if quiz_attempt:
            quiz_questions = json.loads(quiz_attempt.quiz_questions)
        else:
            try:
                # Generate new quiz questions if none exist
                quiz_questions = ai_service.generate_quiz_questions(daily_word.word)
                
                quiz_attempt = QuizAttempt(
                    user_id=current_user.id,
                    word=daily_word.word,
                    quiz_questions=json.dumps(quiz_questions)
                )
                db.session.add(quiz_attempt)
                db.session.commit()
            except Exception as e:
                flash(f"Error generating quiz questions: {str(e)}", "error")
                quiz_questions = None
    
    # Get previous learned words and quiz history
    previous_words = DailyWord.query.filter_by(user_id=current_user.id).order_by(DailyWord.date_learned.desc()).limit(10).all()
    quiz_history = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.date_attempted.desc()).limit(5).all()
    
    current_quiz_completed = False
    quiz_score = None
    
    # Check if today's quiz has been completed
    if quiz_attempt and quiz_attempt.score is not None:
        current_quiz_completed = True
        quiz_score = quiz_attempt.score
    
    return render_template(
        'dashboard.html', 
        word_data=word_data, 
        quiz_questions=quiz_questions,
        previous_words=previous_words,
        quiz_history=quiz_history,
        learning_streak=current_user.learning_streak,
        current_quiz_completed=current_quiz_completed,
        quiz_score=quiz_score
    )

@bp.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    word = request.form.get('word')
    
    # Get today's quiz attempt for this word
    today = datetime.utcnow().date()
    quiz_attempt = QuizAttempt.query.filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.word == word,
        db.func.date(QuizAttempt.date_attempted) == today
    ).first()
    
    if quiz_attempt:
        # Extract answers from form
        form_data = {k: v for k, v in request.form.items() if k != 'word'}
        
        # Calculate score
        quiz_questions = json.loads(quiz_attempt.quiz_questions)
        score = calculate_quiz_score(quiz_questions, form_data)
        
        # Update quiz attempt
        quiz_attempt.user_answers = json.dumps(form_data)
        quiz_attempt.score = score
        
        # Update streak
        current_user.update_learning_streak()
        
        db.session.commit()
        
        flash(f'Quiz submitted! Your score: {score:.1f}%')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        interests = request.form.get('interests')
        difficulty = request.form.get('difficulty')
        
        current_user.interests = interests
        current_user.preferred_difficulty = difficulty
        
        db.session.commit()
        flash('Settings updated successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('settings.html', user=current_user)

def calculate_quiz_score(quiz_questions, user_answers):
    """Calculate the user's score on a quiz"""
    if not quiz_questions or not user_answers:
        return 0
    
    correct_answers = 0
    total_questions = len(quiz_questions)
    
    for question in quiz_questions:
        question_text = question['question']
        if user_answers.get(question_text) == question['correct_answer']:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100 if total_questions > 0 else 0