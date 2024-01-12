from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .utils import generate_unique_filename
from .main_static import main_static_bp
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='/var/lib/docker/volumes/vendify-uploads', static_url_path='/uploads')

    # Secret key
    app.config['SECRET_KEY'] = 'aabbccddeeffgg'

    # Upload folder
    app.config['UPLOAD_FOLDER'] = '/var/lib/docker/volumes/vendify-uploads'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/docker/volumes/vendify-data/vendify-data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    from website.admin_utils import create_admin_user

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from website.models import User
        user = User.query.get(int(user_id))
        if user and user.is_active:  # Check if the user is active
            return user
        return None

    from .user import user
    from .auth import auth
    from .admin import admin
    from .vendor import vendor
    app.register_blueprint(user)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(vendor)
    app.register_blueprint(main_static_bp)

    with app.app_context():
        db.create_all()
        create_admin_user()

    return app
