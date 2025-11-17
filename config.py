import os

# Try to load dotenv if available, otherwise skip (for backwards compatibility)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except ImportError:
    # python-dotenv not installed, use environment variables directly
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    #ImposterAmongus
class Config:
    # Use environment variable for SECRET_KEY, fallback to a default only in development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/assignments')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'jpg', 'jpeg', 'png'}
    SUBMISSION_FOLDER = os.path.join(BASE_DIR, 'static/uploads/submissions')
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    
    # Maximum file upload size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Admin security - whitelist of authorized admin emails/usernames
    # Only these emails/usernames can register as admin or be granted admin role
    # Format: comma-separated list, e.g., "admin@example.com,superadmin@example.com,admin_user"
    ADMIN_WHITELIST = os.environ.get('ADMIN_WHITELIST', '').split(',') if os.environ.get('ADMIN_WHITELIST') else []
    # Clean up whitespace and filter empty strings
    ADMIN_WHITELIST = [item.strip().lower() for item in ADMIN_WHITELIST if item.strip()]