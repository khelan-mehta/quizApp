from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.models import User, Subject, Chapter, Quiz, Question, Score, db
from datetime import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure only admin can access routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    stats = {
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_subjects': Subject.query.count(),
        'total_chapters': Chapter.query.count(),
        'total_quizzes': Quiz.query.count(),
        'total_questions': Question.query.count(),
        'total_attempts': Score.query.count()
    }
    
    # Recent activities
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    recent_attempts = Score.query.order_by(Score.time_stamp_of_attempt.desc()).limit(5).all()
    
    subjects = Subject.query.all()

    # Pass everything to the dashboard template
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_users=recent_users,
                           recent_attempts=recent_attempts,
                           subjects=subjects)

@admin_bp.route('/subjects')
@admin_required
def subjects():
    """Manage subjects"""
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@admin_bp.route('/subjects/add', methods=['POST'])
@admin_required
def add_subject():
    """Add new subject"""
    name = request.form['name']
    description = request.form['description']
    
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    """Delete subject"""
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/chapters/<int:subject_id>')
@admin_required
def chapters(subject_id):
    """Manage chapters for a subject"""
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/chapters.html', subject=subject, chapters=chapters)

@admin_bp.route('/chapters/add', methods=['POST'])
@admin_required
def add_chapter():
    """Add new chapter"""
    name = request.form['name']
    description = request.form.get('description', '')  # Use get() with default
    subject_id = request.form['subject_id']
    
    # Validate that the subject exists
    subject = Subject.query.get_or_404(subject_id)
    
    try:
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        
        flash(f'Chapter "{name}" added successfully to {subject.name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding chapter. Please try again.', 'error')
    
    return redirect(url_for('admin.chapters', subject_id=subject_id))

@admin_bp.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    """Delete chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id  # Store before deletion
    
    try:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting chapter. Please try again.', 'error')
    
    return redirect(url_for('admin.chapters', subject_id=subject_id))

@admin_bp.route('/quizzes/<int:chapter_id>')
@admin_required
def quizzes(chapter_id):
    """Manage quizzes for a chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('admin/quizzes.html', chapter=chapter, quizzes=quizzes)

@admin_bp.route('/create_quiz/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def create_quiz(chapter_id):
    """Create a new quiz with questions and live date range"""
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        title = request.form['title']
        live_from = datetime.strptime(request.form['live_from'], '%Y-%m-%dT%H:%M')
        live_to = datetime.strptime(request.form['live_to'], '%Y-%m-%dT%H:%M')
        time_duration = request.form['time_duration']
        remarks = request.form.get('remarks', '')

        quiz = Quiz(
            title=title,
            chapter_id=chapter_id,
            date_of_quiz=live_from.date(),
            time_duration=time_duration,
            remarks=remarks,
            live_from=live_from,
            live_to=live_to
        )
        db.session.add(quiz)
        db.session.flush()

        # Add questions
        question_count = int(request.form.get('question_count', 1))
        for i in range(1, question_count + 1):
            question_text = request.form.get(f'question_{i}')
            if question_text:
                option1 = request.form.get(f'option1_{i}')
                option2 = request.form.get(f'option2_{i}')
                option3 = request.form.get(f'option3_{i}')
                option4 = request.form.get(f'option4_{i}')
                correct_option = int(request.form.get(f'correct_option_{i}', 1))

                question = Question(
                    quiz_id=quiz.id,
                    question_statement=question_text,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_option=correct_option
                )
                db.session.add(question)

        db.session.commit()
        flash('Quiz and questions added successfully!', 'success')
        return redirect(url_for('admin.quizzes', chapter_id=chapter_id))

    return render_template('admin/create_quiz.html', chapter=chapter)

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/chapters_redirect')
@admin_required
def chapters_redirect():
    """Redirect to chapters page after selecting subject"""
    subject_id = request.args.get('subject_id')
    if subject_id and subject_id.isdigit():
        return redirect(url_for('admin.chapters', subject_id=int(subject_id)))
    flash('Please select a valid subject.', 'error')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/search')
@admin_required
def search():
    """Search across users, subjects, and quizzes"""
    query = request.args.get('q', '')
    results = {
        'users': User.query.filter(User.username.ilike(f'%{query}%')).all() if query else [],
        'subjects': Subject.query.filter(Subject.name.ilike(f'%{query}%')).all() if query else [],
        'quizzes': Quiz.query.filter(Quiz.title.ilike(f'%{query}%')).all() if query else []
    }
    return render_template('admin/search.html', query=query, results=results)