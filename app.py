# app.py
from flask import Flask, render_template, send_from_directory
from config import Config
from extensions import db, login_manager, csrf
import os
import logging
from logging.handlers import RotatingFileHandler

# Try to import Flask-Migrate (optional)
try:
    from flask_migrate import Migrate
    migrate = Migrate()
except ImportError:
    migrate = None


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    # Upload Configuration - ADDED
    app.config['UPLOAD_FOLDER'] = app.config.get(
        'UPLOAD_FOLDER', 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {
        'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

    # Ensure upload folders exist - UPDATED
    upload_folders = [
        app.config.get("UPLOAD_FOLDER", "static/uploads"),
        os.path.join(app.config.get("UPLOAD_FOLDER",
                     "static/uploads"), "avatars"),
        app.config.get("UPLOAD_FOLDER", "static/uploads/assignments"),
        app.config.get("SUBMISSION_FOLDER", "static/uploads/submissions")
    ]

    for folder in upload_folders:
        os.makedirs(folder, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.session_protection = 'strong'
    csrf.init_app(app)  # Initialize CSRF protection

    # Initialize Flask-Migrate if available
    if migrate:
        migrate.init_app(app, db)

    # Make CSRF token function available in templates
    @app.context_processor
    def inject_csrf():
        from flask_wtf.csrf import generate_csrf

        def csrf_token():
            return generate_csrf()
        return dict(csrf_token=csrf_token)

    # Flask-WTF automatically accepts CSRF tokens from:
    # 1. Form data (csrf_token field)
    # 2. X-CSRFToken header (for AJAX/JSON requests)

    # Import models so SQLAlchemy recognizes them
    with app.app_context():
        import models.models  # registers User, Teacher, Student, Assignment, Class, Submission

        # Check if database exists and if schema is outdated
        db_file = app.config['SQLALCHEMY_DATABASE_URI'].replace(
            'sqlite:///', '')
        db_exists = os.path.exists(db_file)

        # Drop and recreate all tables if RECREATE_DB environment variable is set
        if os.environ.get('RECREATE_DB', '').lower() == 'true':
            print("WARNING: RECREATE_DB is set to True - dropping all tables...")
            db.drop_all()
            print("SUCCESS: All tables dropped")
        elif db_exists:
            # Check if schema is outdated by testing queries on multiple models
            schema_outdated = False
            try:
                from models.user import User
                from models.class_model import Class
                # Try to query both User and Class - if either fails, schema is outdated
                test_user = User.query.first()
                test_class = Class.query.first()
            except Exception as e:
                error_str = str(e).lower()
                if 'no such column' in error_str or 'no such table' in error_str:
                    print(
                        "WARNING: Detected outdated database schema. Recreating tables...")
                    print(f"   Error: {str(e)[:150]}")
                    schema_outdated = True
                else:
                    raise

            if schema_outdated:
                db.drop_all()
                print("SUCCESS: Old tables dropped")

        db.create_all()
        print("SUCCESS: Database tables created/verified")

    # Define user loader AFTER models are imported
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Home route — redirects or shows welcome page
    @app.route('/')
    def home():
        return render_template('home.html')

    # Serve favicon at /favicon.ico to avoid 404 requests
    @app.route('/favicon.ico')
    def favicon():
        # Use the site's login illustration as a simple favicon fallback
        return send_from_directory(os.path.join(app.root_path, 'static', 'uploads', 'images'),
                                   'login-illustration.png', mimetype='image/png')

    # Helper function for file uploads - ADDED
    def allowed_file(filename):
        """Check if uploaded file has an allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower(
               ) in app.config['ALLOWED_EXTENSIONS']

    # Make it available to the app context
    app.allowed_file = allowed_file

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}', exc_info=True)
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app


app = create_app()

if __name__ == '__main__':
    # Only run in debug mode if explicitly set via environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Use Render-provided port or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Bind to all interfaces so Render can reach the app
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
