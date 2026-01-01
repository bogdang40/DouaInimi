"""Custom decorators for route protection."""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def email_verified_required(f):
    """Decorator that requires user to have verified email.

    Use this on routes where email verification is mandatory,
    such as discover, matches, and messaging.

    Usage:
        @app.route('/protected')
        @login_required
        @email_verified_required
        def protected():
            return 'Only verified users can see this'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if not current_user.is_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('auth.verification_pending'))

        return f(*args, **kwargs)
    return decorated_function


def profile_complete_required(f):
    """Decorator that requires user to have a complete profile.

    Use this on routes where profile completion is mandatory,
    such as discover and matching features.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if not current_user.profile or not current_user.profile.is_complete:
            flash('Please complete your profile to access this feature.', 'info')
            return redirect(url_for('profile.edit'))

        return f(*args, **kwargs)
    return decorated_function


def approved_required(f):
    """Decorator that requires user account to be approved by admin.

    Use this on routes where admin approval is required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        if not current_user.is_approved:
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('main.dashboard'))

        return f(*args, **kwargs)
    return decorated_function
