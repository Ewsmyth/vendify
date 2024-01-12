from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
import os
import uuid
from datetime import datetime

# This decorator only allows admins access to the page
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.index'))
        if current_user.authority == 'user':
            flash('Users cannot access admin pages.')
            return redirect(url_for('user.home'))
        elif current_user.authority == 'vendor':
            flash('Vendors cannot access admin pages.')
            return redirect(url_for('vendor.vendorpage'))

        return f(*args, **kwargs)

    return decorated_function

# This decorator only allows users to access the page
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.index'))
        if current_user.authority == 'admin':
            flash('Admins cannot access user pages.')
            return redirect(url_for('admin.adminpage'))
        elif current_user.authority == 'vendor':
            flash('Vendors cannot access user pages.')
            return redirect(url_for('vendor.vendorpage'))

        return f(*args, **kwargs)

    return decorated_function

# This decorator only allows vendors to access the page
def vendor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.index'))
        if current_user.authority == 'user':
            flash('Users cannot access vendor pages.')
            return redirect(url_for('user.home'))
        elif current_user.authority == 'admin':
            flash('Admins cannot access vendor pages.')
            return redirect(url_for('admin.adminpage'))

        return f(*args, **kwargs)

    return decorated_function

# This decorator generates a unique filename
def generate_unique_filename(username, file_extension):
    current_time = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    random_digits = str(uuid.uuid4().int & (1 << 32) - 1).zfill(5)
    return f"{username}_{current_time}_{random_digits}.{file_extension}"