from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User and Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find user in database
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # In production, use proper password hashing
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session['full_name'] = user.full_name
            
            if user.is_admin:
                flash('Welcome, Quiz Master!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash(f'Welcome, {user.full_name}!', 'success')
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (not for admin)"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(
            username=username,
            password=password,  # In production, hash the password
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))