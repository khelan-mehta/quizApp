from flask import Flask, render_template, redirect, url_for, session
import os
from datetime import datetime
from database.models import db  # Import db after models setup
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with app
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    @app.route('/')
    def index():
        """Home page - redirect to login"""
        return redirect(url_for('auth.login'))

    # Define initialization function
    def create_tables():
        """Create database tables and admin user"""
        with app.app_context():
            db.create_all()
            from database.models import User
            admin = User.query.filter_by(username='admin@quizmaster.com').first()
            if not admin:
                admin = User(
                    username='admin@quizmaster.com',
                    password='admin123',  # Use proper hashing in production
                    full_name='Quiz Master Admin',
                    qualification='Administrator',
                    dob=datetime(1990, 1, 1),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created: admin@quizmaster.com / admin123")

    # Call initialization
    with app.app_context():
        create_tables()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)