from website.models import User
from website import db

def create_admin_user():
    # Check if an admin user already exists
    admin = User.query.filter_by(authority='admin').first()
    if not admin:
        # If no admin user exists, create one
        admin = User(
            username='admin',
            password='password',
            authority='admin',
            is_active=True
        )
        admin.set_password('password')  # Hash the password
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")    