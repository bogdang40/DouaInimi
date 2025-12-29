"""Flask application factory."""
import os
from flask import Flask
from flask_socketio import SocketIO

from app.config import config
from app.extensions import db, migrate, login_manager, bcrypt, mail, csrf, init_limiter

socketio = SocketIO()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize rate limiter
    limiter = init_limiter(app)
    if limiter:
        app.limiter = limiter
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.discover import discover_bp
    from app.routes.matches import matches_bp
    from app.routes.messages import messages_bp
    from app.routes.settings import settings_bp
    from app.routes.admin import admin_bp
    from app.routes.safety import safety_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(discover_bp, url_prefix='/discover')
    app.register_blueprint(matches_bp, url_prefix='/matches')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(safety_bp, url_prefix='/safety')
    
    # User loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Update last_active on each request (for online status)
    @app.before_request
    def update_user_activity():
        from flask_login import current_user
        from datetime import datetime
        
        if current_user.is_authenticated:
            # Only update if more than 30 seconds since last update
            if not current_user.last_active or \
               (datetime.utcnow() - current_user.last_active).total_seconds() > 30:
                current_user.last_active = datetime.utcnow()
                db.session.commit()
    
    # Context processors
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        
        context = {
            'app_name': app.config.get('APP_NAME', 'Două Inimi'),
        }
        
        # Add unread counts for authenticated users
        if current_user.is_authenticated:
            from app.models.match import Match
            from app.models.message import Message
            
            # Get total unread message count
            total_unread = 0
            matches = Match.get_user_matches(current_user.id)
            for match in matches:
                total_unread += match.unread_count(current_user.id)
            
            context['total_unread_messages'] = total_unread
            context['user_matches_count'] = len(matches)
        
        return context
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection (for older browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (disable unnecessary features)
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (allow what we need)
        if not app.debug:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.socket.io https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://static.cloudflareinsights.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' wss: ws: https://unpkg.com https://cdn.socket.io https://cloudflareinsights.com; "
                "frame-ancestors 'self';"
            )
            response.headers['Content-Security-Policy'] = csp
        
        return response
    
    # Create tables in development
    with app.app_context():
        db.create_all()
    
    return app

