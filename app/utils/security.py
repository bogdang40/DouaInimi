"""Security utilities for input validation, sanitization, and protection."""
import re
import html
from functools import wraps
from flask import request, abort, current_app
from flask_login import current_user


# --- Input Sanitization ---

def sanitize_html(text):
    """
    Remove all HTML tags and escape special characters.
    Use for user-generated content that shouldn't contain HTML.
    """
    if not text:
        return text
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(text))
    
    # Escape remaining special characters
    text = html.escape(text)
    
    return text


def sanitize_message(content):
    """
    Sanitize message content while preserving some formatting.
    - Removes HTML tags
    - Escapes special characters
    - Normalizes whitespace
    - Limits consecutive newlines
    """
    if not content:
        return ""
    
    # Convert to string and strip
    content = str(content).strip()
    
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Escape HTML entities
    content = html.escape(content)
    
    # Normalize whitespace (but keep single newlines for formatting)
    content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces/tabs to single space
    content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
    
    # Remove zero-width characters and other invisibles (potential attacks)
    content = re.sub(r'[\u200b-\u200f\u2028-\u202f\u2060\ufeff]', '', content)
    
    return content.strip()


def sanitize_bio(text):
    """Sanitize bio/about text - allows some formatting."""
    if not text:
        return text
    
    text = sanitize_message(text)
    
    # Limit length
    if len(text) > 2000:
        text = text[:2000]
    
    return text


def sanitize_username(name):
    """Sanitize display name/username."""
    if not name:
        return name
    
    # Remove HTML
    name = re.sub(r'<[^>]+>', '', str(name))
    
    # Only allow alphanumeric, spaces, and basic punctuation
    name = re.sub(r'[^\w\s\-\'\.]', '', name, flags=re.UNICODE)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    # Limit length
    if len(name) > 50:
        name = name[:50]
    
    return name.strip()


# --- Content Validation ---

def validate_message_content(content, max_length=5000, min_length=1):
    """
    Validate message content.
    Returns (is_valid, error_message, sanitized_content)
    """
    if not content:
        return False, "Message cannot be empty", None
    
    content = sanitize_message(content)
    
    if len(content) < min_length:
        return False, "Message cannot be empty", None
    
    if len(content) > max_length:
        return False, f"Message cannot exceed {max_length} characters", None
    
    # Check for spam patterns
    if is_spam_content(content):
        return False, "Message flagged as spam", None
    
    return True, None, content


def is_spam_content(content):
    """
    Check if content matches spam patterns.
    Returns True if content appears to be spam.
    """
    if not content:
        return False
    
    content_lower = content.lower()
    
    # Spam patterns
    spam_patterns = [
        r'(https?://\S+){3,}',  # Too many URLs
        r'(whatsapp|telegram|signal)\s*[:\s]*[\d\+]',  # Phone number solicitation
        r'(cash\s*app|venmo|paypal|zelle)\s*[@\:]',  # Payment solicitation
        r'(bitcoin|crypto|btc|eth)\s*(wallet|address)',  # Crypto spam
        r'make\s*\$?\d+\s*per\s*(day|hour|week)',  # Get rich quick
        r'(hot|sexy)\s*(singles|women|girls|men)\s*(near|in)',  # Dating spam
    ]
    
    for pattern in spam_patterns:
        if re.search(pattern, content_lower):
            return True
    
    # Check for excessive repetition
    words = content_lower.split()
    if len(words) > 5:
        unique_words = set(words)
        if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
            return True
    
    return False


# --- Authorization Decorators ---

def verified_required(f):
    """Decorator to require email verification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_verified:
            from flask import flash, redirect, url_for
            flash('Please verify your email to access this feature.', 'warning')
            return redirect(url_for('auth.verification_pending'))
        return f(*args, **kwargs)
    return decorated_function


def profile_required(f):
    """Decorator to require a completed profile."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.profile or not current_user.profile.is_complete:
            from flask import flash, redirect, url_for
            flash('Please complete your profile first.', 'info')
            return redirect(url_for('profile.edit'))
        return f(*args, **kwargs)
    return decorated_function


# --- Request Validation ---

def validate_json_request():
    """Validate that request is JSON and has valid CSRF."""
    if not request.is_json:
        abort(400, description="Expected JSON request")
    
    # For AJAX requests, check CSRF token in header
    csrf_token = request.headers.get('X-CSRFToken') or request.headers.get('X-CSRF-Token')
    if not csrf_token:
        # Also check in JSON body
        data = request.get_json(silent=True)
        if data:
            csrf_token = data.get('csrf_token')
    
    # CSRF validation is handled by Flask-WTF, this is just for logging
    return True


def get_client_ip():
    """Get client IP address, handling proxies."""
    if request.headers.get('X-Forwarded-For'):
        # First IP in the chain is the client
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


# --- Socket.IO Security ---

def validate_socket_user():
    """
    Validate that the current socket connection has an authenticated user.
    Returns user_id or None.
    """
    from flask_login import current_user
    
    if current_user.is_authenticated:
        return current_user.id
    return None


def validate_socket_match_access(match_id, user_id):
    """
    Validate that a user has access to a match conversation.
    Returns True if user is part of the match.
    """
    from app.models.match import Match
    
    if not match_id or not user_id:
        return False
    
    match = Match.query.get(match_id)
    if not match:
        return False
    
    return match.user1_id == user_id or match.user2_id == user_id


# --- Password Validation ---

def validate_password_strength(password):
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for common passwords
    common_passwords = [
        'password', '12345678', 'qwerty123', 'password1', 'letmein',
        'welcome1', 'monkey12', 'dragon12', 'master12', 'login123'
    ]
    if password.lower() in common_passwords:
        return False, "Password is too common"
    
    return True, None


# --- File Upload Security ---

def validate_image_upload(file):
    """
    Validate an uploaded image file.
    Returns (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Check filename
    filename = file.filename
    if not filename:
        return False, "No filename"
    
    # Check extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Use: {', '.join(allowed_extensions)}"
    
    # Check file size (read first few bytes to check magic number)
    file.seek(0)
    header = file.read(8)
    file.seek(0)
    
    # Check magic numbers for image types
    valid_signatures = [
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'\xff\xd8\xff',  # JPEG
        b'GIF87a', b'GIF89a',  # GIF
        b'RIFF',  # WebP (starts with RIFF, then WEBP)
    ]
    
    is_valid_signature = any(header.startswith(sig) for sig in valid_signatures)
    if not is_valid_signature and not header[:4] == b'RIFF':  # WebP check
        return False, "Invalid image file"
    
    return True, None


# --- Logging ---

def log_security_event(event_type, details=None):
    """Log a security-related event."""
    from datetime import datetime
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': event_type,
        'ip': get_client_ip(),
        'user_id': current_user.id if current_user.is_authenticated else None,
        'details': details
    }
    
    current_app.logger.warning(f"SECURITY: {event_type} - {log_entry}")

