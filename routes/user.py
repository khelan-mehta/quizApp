from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import User, Subject, Chapter, Quiz, Question, Score, db
from datetime import datetime
from functools import wraps

user_bp = Blueprint('user', __name__)

def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with personal statistics"""
    user_id = session['user_id']
    
    # Get user statistics
    total_attempts = Score.query.filter_by(user_id=user_id).count()
    recent_attempts = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
    
    # Calculate average score
    scores = Score.query.filter_by(user_id=user_id).all()
    avg_score = 0
    if scores:
        avg_score = sum([score.percentage for score in scores]) / len(scores)
    
    # Get available subjects and quizzes
    available_subjects = Subject.query.all()
    total_quizzes = Quiz.query.count()
    
    stats = {
        'total_attempts': total_attempts,
        'average_score': round(avg_score, 2),
        'available_subjects': len(available_subjects),
        'total_quizzes': total_quizzes
    }
    
    return render_template('user/dashboard.html', 
                         stats=stats, 
                         recent_attempts=recent_attempts,
                         subjects=available_subjects)

@user_bp.route('/quiz-list')
@login_required
def quiz_list():
    """Display all available quizzes organized by subject"""
    subjects = Subject.query.all()
    return render_template('user/quiz_list.html', subjects=subjects)

@user_bp.route('/quiz/<int:quiz_id>/start')
@login_required
def start_quiz(quiz_id):
    """Start a quiz attempt"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    if not questions:
        flash('This quiz has no questions yet!', 'error')
        return redirect(url_for('user.quiz_list'))
    
    # Store quiz start time in session
    session['quiz_start_time'] = datetime.now().isoformat()
    session['current_quiz_id'] = quiz_id
    
    return render_template('user/quiz_attempt.html', quiz=quiz, questions=questions)

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz and calculate score"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    user_id = session['user_id']
    
    # Calculate score
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and int(user_answer) == question.correct_option:
            correct_answers += 1
    
    # Calculate time taken
    start_time = datetime.fromisoformat(session.get('quiz_start_time', datetime.now().isoformat()))
    end_time = datetime.now()
    time_taken = str(end_time - start_time).split('.')[0]  # Remove microseconds
    
    # Save score
    score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        total_scored=correct_answers,
        total_questions=total_questions,
        time_taken=time_taken
    )
    db.session.add(score)
    db.session.commit()
    
    # Clear session data
    session.pop('quiz_start_time', None)
    session.pop('current_quiz_id', None)
    
    flash(f'Quiz submitted! You scored {correct_answers}/{total_questions}', 'success')
    return redirect(url_for('user.quiz_result', score_id=score.id))

@user_bp.route('/quiz/result/<int:score_id>')
@login_required
def quiz_result(score_id):
    """Display quiz result"""
    score = Score.query.get_or_404(score_id)
    
    # Ensure user can only view their own results
    if score.user_id != session['user_id']:
        flash('Access denied!', 'error')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/quiz_result.html', score=score)

@user_bp.route('/results')
@login_required
def results():
    """Display all user's quiz results"""
    user_id = session['user_id']
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.time_stamp_of_attempt.desc()).all()
    
    return render_template('user/results.html', scores=scores)

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = User.query.get_or_404(session['user_id'])
    return render_template('user/profile.html', user=user)

@user_bp.route('/chapter/<int:chapter_id>/quizzes')
@login_required
def quizzes_by_chapter(chapter_id):
    """Display quizzes under a specific chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('user/quizzes_by_chapter.html', chapter=chapter, quizzes=quizzes)


@user_bp.route('/subject/<int:subject_id>/chapters')
@login_required
def subject_chapters(subject_id):
    """Display chapters and quizzes for a subject"""
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return render_template('user/subject_chapters.html', subject=subject, chapters=chapters)