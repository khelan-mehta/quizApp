#!/usr/bin/env python3
"""
Quiz Master Setup Script
This script sets up the Quiz Master application with sample data
"""

import os
import sys
from datetime import datetime, date

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        'database',
        'routes',
        'templates/auth',
        'templates/admin',
        'templates/user',
        'static/css',
        'static/js',
        'static/images',
        'utils'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory in ['database', 'routes', 'utils']:
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('# -*- coding: utf-8 -*-\n')
    
    print("✓ Directory structure created")

def create_sample_data():
    """Create sample data for testing"""
    try:
        # Import after ensuring app is properly set up
        from app import app, db
        from database.models import User, Subject, Chapter, Quiz, Question
        
        with app.app_context():
            # Create tables
            db.create_all()
            
            # Create admin user if not exists
            admin = User.query.filter_by(username='admin@quizmaster.com').first()
            if not admin:
                admin = User(
                    username='admin@quizmaster.com',
                    password='admin123',
                    full_name='Quiz Master Admin',
                    qualification='Administrator',
                    dob=date(1990, 1, 1),
                    is_admin=True
                )
                db.session.add(admin)
            
            # Create sample users
            sample_users = [
                {
                    'username': 'john.doe@example.com',
                    'password': 'password123',
                    'full_name': 'John Doe',
                    'qualification': 'B.Tech Computer Science',
                    'dob': date(1995, 5, 15)
                },
                {
                    'username': 'jane.smith@example.com',
                    'password': 'password123',
                    'full_name': 'Jane Smith',
                    'qualification': 'M.Sc Mathematics',
                    'dob': date(1993, 8, 22)
                }
            ]
            
            for user_data in sample_users:
                if not User.query.filter_by(username=user_data['username']).first():
                    user = User(**user_data, is_admin=False)
                    db.session.add(user)
            
            # Create sample subjects
            subjects_data = [
                {
                    'name': 'Computer Science',
                    'description': 'Fundamentals of Computer Science and Programming'
                },
                {
                    'name': 'Mathematics',
                    'description': 'Basic and Advanced Mathematical Concepts'
                },
                {
                    'name': 'Physics',
                    'description': 'Classical and Modern Physics Principles'
                }
            ]
            
            for subject_data in subjects_data:
                if not Subject.query.filter_by(name=subject_data['name']).first():
                    subject = Subject(**subject_data)
                    db.session.add(subject)
                    db.session.commit()  # Commit to get ID
                    
                    # Add sample chapters
                    if subject_data['name'] == 'Computer Science':
                        chapters = [
                            {'name': 'Programming Basics', 'description': 'Introduction to Programming'},
                            {'name': 'Data Structures', 'description': 'Arrays, Lists, Trees, Graphs'},
                            {'name': 'Algorithms', 'description': 'Sorting, Searching, Dynamic Programming'}
                        ]
                    elif subject_data['name'] == 'Mathematics':
                        chapters = [
                            {'name': 'Algebra', 'description': 'Linear Algebra and Abstract Algebra'},
                            {'name': 'Calculus', 'description': 'Differential and Integral Calculus'},
                            {'name': 'Statistics', 'description': 'Probability and Statistical Analysis'}
                        ]
                    else:  # Physics
                        chapters = [
                            {'name': 'Mechanics', 'description': 'Classical Mechanics and Motion'},
                            {'name': 'Thermodynamics', 'description': 'Heat and Energy Transfer'},
                            {'name': 'Electromagnetism', 'description': 'Electric and Magnetic Fields'}
                        ]
                    
                    for chapter_data in chapters:
                        chapter = Chapter(**chapter_data, subject_id=subject.id)
                        db.session.add(chapter)
                        db.session.commit()  # Commit to get ID
                        
                        # Add sample quiz
                        quiz = Quiz(
                            title=f"{chapter_data['name']} Quiz",
                            chapter_id=chapter.id,
                            date_of_quiz=date.today(),
                            time_duration="01:00",
                            remarks="Sample quiz for testing purposes"
                        )
                        db.session.add(quiz)
                        db.session.commit()  # Commit to get ID
                        
                        # Add sample questions
                        if chapter_data['name'] == 'Programming Basics':
                            questions = [
                                {
                                    'question_statement': 'What is the correct way to declare a variable in Python?',
                                    'option1': 'var x = 5',
                                    'option2': 'x = 5',
                                    'option3': 'int x = 5',
                                    'option4': 'declare x = 5',
                                    'correct_option': 2
                                },
                                {
                                    'question_statement': 'Which of the following is NOT a primitive data type in Python?',
                                    'option1': 'int',
                                    'option2': 'float',
                                    'option3': 'string',
                                    'option4': 'list',
                                    'correct_option': 4
                                }
                            ]
                        else:
                            # Generic sample questions
                            questions = [
                                {
                                    'question_statement': f'Sample question 1 for {chapter_data["name"]}?',
                                    'option1': 'Option A',
                                    'option2': 'Option B',
                                    'option3': 'Option C',
                                    'option4': 'Option D',
                                    'correct_option': 1
                                },
                                {
                                    'question_statement': f'Sample question 2 for {chapter_data["name"]}?',
                                    'option1': 'Option A',
                                    'option2': 'Option B',
                                    'option3': 'Option C',
                                    'option4': 'Option D',
                                    'correct_option': 2
                                }
                            ]
                        
                        for question_data in questions:
                            question = Question(**question_data, quiz_id=quiz.id)
                            db.session.add(question)
            
            db.session.commit()
            print("✓ Sample data created successfully")
            print("\nLogin Credentials:")
            print("Admin: admin@quizmaster.com / admin123")
            print("User 1: john.doe@example.com / password123")
            print("User 2: jane.smith@example.com / password123")
            
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        return False
    
    return True

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import flask_sqlalchemy
        print(f"✓ Flask {flask.__version__} installed")
        print(f"✓ Flask-SQLAlchemy installed")
        return True
    except ImportError as e:
        print(f"✗ Missing requirement: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def create_run_script():
    """Create a simple run script"""
    run_script = """#!/usr/bin/env python3
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("Starting Quiz Master Application...")
    print("Access the application at: http://localhost:5000")
    print("Admin login: admin@quizmaster.com / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    with open('run.py', 'w') as f:
        f.write(run_script)
    
    # Make it executable on Unix systems
    if os.name != 'nt':
        os.chmod('run.py', 0o755)
    
    print("✓ Run script created (run.py)")

def main():
    """Main setup function"""
    print("Quiz Master Application Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create directory structure
    create_directory_structure()
    
    # Create run script
    create_run_script()
    
    # Create sample data
    if create_sample_data():
        print("\n" + "=" * 40)
        print("Setup completed successfully!")
        print("\nTo start the application:")
        print("1. python run.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Login with admin credentials")
        print("\nFor development:")
        print("- Edit templates in templates/ directory")
        print("- Add CSS in static/css/style.css")
        print("- Modify routes in routes/ directory")
    else:
        print("\n✗ Setup completed with errors")
        sys.exit(1)

if __name__ == '__main__':
    main()