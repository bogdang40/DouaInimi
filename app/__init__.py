"""Flask application factory."""
import os
import time
import logging
from flask import Flask, g, request
from flask_socketio import SocketIO

from app.config import config
from app.extensions import db, migrate, login_manager, bcrypt, mail, csrf, init_limiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # Use threading mode for Socket.IO - compatible with Azure App Service
    # Falls back to long-polling which works reliably with gthread workers
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode='threading',  # Threading mode works with gthread workers
        ping_timeout=30,         # Reduced timeout for faster reconnection
        ping_interval=15,        # More frequent pings for better connection health
        logger=False,            # Reduce logging noise
        engineio_logger=False
    )
    
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
    
    # Request timing - start timer
    @app.before_request
    def start_timer():
        g.start_time = time.time()
        g.query_count = 0

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
        # OPTIMIZED: Single query instead of N+1
        if current_user.is_authenticated:
            from app.models.match import Match
            from app.models.message import Message
            from sqlalchemy import func, and_

            # Single efficient query to get both total unread and match count
            result = db.session.query(
                func.count(func.distinct(Match.id)).label('match_count'),
                func.coalesce(func.sum(
                    db.session.query(func.count(Message.id))
                    .filter(
                        Message.match_id == Match.id,
                        Message.sender_id != current_user.id,
                        Message.is_read == False
                    )
                    .correlate(Match)
                    .scalar_subquery()
                ), 0).label('total_unread')
            ).filter(
                db.or_(Match.user1_id == current_user.id, Match.user2_id == current_user.id),
                Match.is_active == True
            ).first()

            context['user_matches_count'] = result.match_count if result else 0
            context['total_unread_messages'] = int(result.total_unread) if result and result.total_unread else 0

        return context

    # Request timing logging
    @app.after_request
    def log_request_timing(response):
        # Skip static files and socket.io
        if request.path.startswith('/static') or request.path.startswith('/socket.io'):
            return response

        if hasattr(g, 'start_time'):
            elapsed = (time.time() - g.start_time) * 1000  # Convert to ms

            # Get query info from Flask-SQLAlchemy
            from flask_sqlalchemy.record_queries import get_recorded_queries
            try:
                queries = get_recorded_queries()
                query_count = len(queries)
                total_query_time = sum(q.duration * 1000 for q in queries)  # ms

                # Log slow requests (> 500ms) or any request with many queries
                if elapsed > 500 or query_count > 5:
                    logger.warning(
                        f"SLOW REQUEST: {request.method} {request.path} "
                        f"| Total: {elapsed:.0f}ms | Queries: {query_count} ({total_query_time:.0f}ms)"
                    )
                    # Log individual slow queries (> 50ms)
                    for q in queries:
                        if q.duration * 1000 > 50:
                            logger.warning(f"  SLOW QUERY ({q.duration*1000:.0f}ms): {q.statement[:200]}")
                else:
                    logger.info(
                        f"REQUEST: {request.method} {request.path} "
                        f"| Total: {elapsed:.0f}ms | Queries: {query_count}"
                    )
            except Exception as e:
                logger.info(f"REQUEST: {request.method} {request.path} | Total: {elapsed:.0f}ms (query logging error: {e})")

        return response

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

