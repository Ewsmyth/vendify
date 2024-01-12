from flask import Blueprint, send_from_directory, request, session, jsonify
import os

# Define a blueprint for the main project static files
main_static_bp = Blueprint('main_static', __name__)

@main_static_bp.route('/project_static/<path:filename>')
def project_static(filename):
    project_static_folder = os.path.join(os.getcwd(), 'website')  # Change this path to match your project structure
    return send_from_directory(project_static_folder, filename)

@main_static_bp.route('/set_theme', methods=['POST'])
def set_theme():
    theme = request.json.get('theme')
    session['theme'] = theme
    return jsonify({'status': 'success'})

@main_static_bp.route('/get_theme', methods=['GET'])
def get_theme():
    theme = session.get('theme', 'light')  # Default to light mode if no theme is set
    return jsonify({'theme': theme})
