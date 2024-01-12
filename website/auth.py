from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from sqlalchemy.exc import IntegrityError
from website import db
from website.models import User, LogEvent
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                if user.authority == 'admin':
                    return redirect(url_for('admin.adminpage', username=username))
                elif user.authority == 'vendor':
                    return redirect(url_for('vendor.vendorpage', username=username))
                elif user.authority == 'user':
                    return redirect(url_for('user.home', username=username))
            else:
                flash('Inactive account, contact support.', 'error')
                return redirect(url_for('auth.login'))  # Redirect back to login page
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))  # Redirect back to login page

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if not username or not password1 or not password2:
            flash('All fields are required', 'error')

        elif password1!= password2:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        else:
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                flash('User already exists', 'error')
                return redirect(url_for('auth.register'))

            user = User(username=username)
            user.set_password(password1)
            db.session.add(user)

            event_description = f"New user '{username}' has registered."
            new_event = LogEvent(event_description=event_description)
            db.session.add(new_event)

            db.session.commit()
            flash('Registration successful, please login.', 'success')
            return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/error')
def error():
    return render_template('error.html')