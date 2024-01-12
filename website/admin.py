from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_required, current_user
from website.models import User, Post, Media, LogEvent
from website import db
from .utils import admin_required
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import os

admin = Blueprint('admin', __name__)

@admin.route('/favicon.ico')
def favicon():
    abort(404)

# The adminpage is the home page for the Admin user's, this page renders event logs
@admin.route('/<username>/adminpage')
@login_required
@admin_required
def adminpage(username):
    recent_events = LogEvent.query.order_by(LogEvent.timestamp.desc()).limit(30).all()
    
    # Format timestamps before passing them to the template
    for event in recent_events:
        event.timestamp_formatted = event.timestamp.strftime('%y/%m/%d %H:%M')
    
    return render_template('adminpage.html', username=username, recent_events=recent_events)

# The users page renders all the user's in the database
@admin.route('/<username>/adminpage/users')
@login_required
@admin_required
def users(username):
    all_users = User.query.all()
    return render_template('users.html', username=username, users=all_users)

# The createuser page allows the admin to create new users, vendors, or admins
@admin.route('/<username>/adminpage/users/createuser', methods=['GET', 'POST'])
@login_required
@admin_required
def createuser(username):
    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        authority = request.form.get('authority')

        if not all([username, password1, password2, authority]):
            flash('Please fill out all fields', 'error')
        elif password1 != password2:
            flash('Passwords do not match', 'warning')
        else:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('User already exists', 'warning')
            else:
                user = User(username=username, authority=authority)
                user.set_password(password1)
                db.session.add(user)

                event_description = f"User '{username}' was created by admin '{current_user.username}'"
                new_event = LogEvent(event_description=event_description)
                db.session.add(new_event)

                db.session.commit()
                flash('User created successfully', 'success')

    return render_template('createuser.html', username=username)

# The update active is a form on the users page that allows the admin to update the user's account status
@admin.route('/update_active/<int:user_id>/<username>', methods=['POST'])
@login_required
@admin_required
def update_active(username, user_id):
    if request.method == 'POST':
        is_active = bool(int(request.form.get('is_active')))
        
        user = User.query.get(user_id)
        if user:
            user.is_active = is_active

            # Log the event for user status update
            event_description = f"Admin '{current_user.id}' updated status of user '{user_id}' ({user.username}) to {is_active}."
            new_event = LogEvent(event_description=event_description)
            db.session.add(new_event)

            db.session.commit()
            flash(f'User {user.username} status updated successfully.', 'success')
        else:
            flash('User not found.', 'error')

        return redirect(url_for('admin.users', username=username))

    # Redirect to users page for GET requests or other scenarios
    return redirect(url_for('admin.users', username=username))

# The update authoity is a form on the users page that allows admins to update a users authority
@admin.route('/update_authority/<int:user_id>/<username>', methods=['POST', 'GET'])
@login_required
@admin_required
def update_authority(username, user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_authority = request.form.get('authority')
    
        user.authority = new_authority

        event_description = f"Admin '{current_user.id}' updated '{user_id}' ({user.username})'s authority to {new_authority}."
        new_event = LogEvent(event_description=event_description)
        db.session.add(new_event)

        db.session.commit()
        flash(f'Authority updated for {user.username}', 'success')
        return redirect(url_for('admin.users', username=username))

    else:
        flash(f'There was an error updating {user.username}\'s authority.', 'error')
        return redirect(url_for('admin.users', username=username))

# This route is for the admin account page that allows them to change their username and password
@admin.route('/<username>/adminpage/account')
@login_required
@admin_required
def account(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.error'))

    return render_template('adminaccount.html', username=username, user=user)

# This is a route for a form so that the admin can change their username
@admin.route('/<username>/adminpage/account/change_username', methods=['POST'])
@login_required
@admin_required
def change_username(username):
    new_username = request.form.get('new_username')

    if not new_username:
        flash('Please provide a new username', 'error')
        return redirect(url_for('admin.account', username=username))

    # Check if the new username already exists in the database
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'warning')
        return redirect(url_for('admin.account', username=username))

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    try:
        # Update the current user's username
        current_user.username = new_username

        # Log the event with user ID
        event_description = f"User '{current_user_id}' changed their username to '{new_username}'."
        new_event = LogEvent(event_description=event_description)
        db.session.add(new_event)

        db.session.commit()

        flash('Username changed successfully!', 'success')
        return render_template('logout_timer.html')

    except Exception as e:
        db.session.rollback()  # Rollback changes in case of an exception
        flash(f'Failed to update username due to a database error: {str(e)}', 'error')
        return redirect(url_for('admin.account', username=username))

# This is a route for the admin account page that allows the admin to change their password with a form
@admin.route('/<username>/adminpage/account/change_password', methods=['POST'])
@login_required
@admin_required
def change_password(username):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if not current_password or not new_password or not confirm_new_password:
        flash('Please provide all password fields', 'warning')
        return redirect(url_for('admin.account', username=username))

    if new_password != confirm_new_password:
        flash('Passwords must match', 'warning')
        return redirect(url_for('admin.account', username=username))

    if not current_user.check_password(current_password):
        flash('Incorrect current password', 'error')
        return redirect(url_for('admin.account', username=username))

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    # Set the new password for the current user
    current_user.set_password(new_password)

    # Log the event with user ID
    event_description = f"User '{current_user_id}' changed their password."
    new_event = LogEvent(event_description=event_description)
    db.session.add(new_event)

    db.session.commit()

    flash('Password changed successfully!', 'success')
    return render_template('logout_timer.html')

# This is a route for a form on the admin account page that allows the admin to change their account status
@admin.route('/<username>/adminpage/account/deactivate_account', methods=['POST'])
@login_required
@admin_required
def deactivate_account(username):

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    # Deactivate the current user's account
    current_user.is_active = False

    # Log the event with user ID
    event_description = f"User '{current_user_id}' deactivated their account."
    new_event = LogEvent(event_description=event_description)
    db.session.add(new_event)

    db.session.commit()

    # You might want to handle additional cleanup or logic here
    flash('Your account has been deactivated', 'success')
    return redirect(url_for('auth.logout'))

@admin.route('/<username>/adminpage/account/update_theme', methods=['POST'])
@login_required
@admin_required
def update_theme(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.error'))

    # Get the theme preference from the form
    theme_preference = request.form.get('theme_preference')

    # Convert the received value to a boolean
    if theme_preference == '1':
        user.theme = True
    else:
        user.theme = False

    # Update the user's theme preference in the database
    db.session.commit()

    flash('Theme preference updated successfully!', 'success')
    return redirect(url_for('admin.account', username=username))
