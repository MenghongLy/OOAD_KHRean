from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Try to import CSRFProtect, make it optional
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
except ImportError:
    # flask-wtf not installed, create a dummy CSRFProtect class
    class CSRFProtect:
        def init_app(self, app):
            pass
    csrf = CSRFProtect()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
