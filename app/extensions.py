"""Flask extensions initialization."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Database
db = SQLAlchemy()

# Database migrations
migrate = Migrate()

# Authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Password hashing
bcrypt = Bcrypt()

# Email
mail = Mail()

# CSRF Protection
csrf = CSRFProtect()

# Rate Limiting (lazy init in app factory)
limiter = None

def init_limiter(app):
    """Initialize rate limiter with app context."""
    global limiter
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://",
        )
        return limiter
    except ImportError:
        app.logger.warning("Flask-Limiter not installed, rate limiting disabled")
        return None

