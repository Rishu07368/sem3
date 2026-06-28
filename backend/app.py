"""
Daily Timetable Engine - Flask Backend
A comprehensive study planning and tracking application.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from datetime import datetime

from models.database import db, Configuration
from routes.api import api


def create_app():
    """Application factory."""
    # Get the directory where this file is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(base_dir, '..', 'frontend', 'build')
    
    app = Flask(__name__, static_folder=build_dir, static_url_path='')
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'timetable.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Initialize default configuration if not exists
        init_default_config()
    
    # Serve React app for non-API routes
    @app.route('/')
    def serve():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        if path.startswith('api/'):
            return {"error": "Not found"}, 404
        static_file = os.path.join(app.static_folder, path)
        if os.path.isfile(static_file):
            return send_from_directory(app.static_folder, path)
        # Fallback to index.html for SPA routing
        return send_from_directory(app.static_folder, 'index.html')
    
    return app


def init_default_config():
    """Initialize default configuration values."""
    defaults = {
        'start_date': '2025-07-14',
        'end_date': '2025-11-10',
        'amcat_start_date': '2025-08-15',
        'amcat_end_date': '2025-09-15',
        'exam_start_date': '2025-11-01',
        'total_available_study_hours': '30.0',
        'exam_weeks_before': '3',
    }
    
    for key, value in defaults.items():
        existing = Configuration.query.filter_by(key=key).first()
        if not existing:
            config = Configuration(key=key, value=value)
            db.session.add(config)
    
    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)