"""Authentication routes."""
from datetime import datetime, timedelta
import secrets
from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target):
    """Check if URL is safe for redirect (same host only)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# Rate limiting decorator (only applies if limiter is available)
def get_limiter():
    """Get limiter from current app or return None."""
    from flask import current_app
    return getattr(current_app, 'limiter', None)


def rate_limit(limit_string):
    """Rate limit decorator that gracefully handles missing limiter."""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = get_limiter()
            if limiter:
                # Apply rate limit
                limited_func = limiter.limit(limit_string)(f)
                return limited_func(*args, **kwargs)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def send_verification_email_safe(user):
    """Try to send verification email, log if fails."""
    try:
        from app.services.email import send_verification_email
        send_verification_email(user)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {e}")
        return False


def send_password_reset_email_safe(user):
    """Try to send password reset email, log if fails."""
    try:
        from app.services.email import send_password_reset_email
        send_password_reset_email(user)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send reset email: {e}")
        return False


@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit("10 per minute")
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # Check if account is locked due to too many failed attempts
        if user and user.is_locked:
            remaining = user.lockout_remaining_minutes
            flash(f'Account temporarily locked. Try again in {remaining} minutes.', 'error')
            return render_template('auth/login.html', form=form)

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)

            # Check if account is approved by admin
            if not user.is_approved:
                flash('Your account is pending admin approval. Please check back later.', 'warning')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            db.session.commit()

            flash('Welcome back!', 'success')

            # Safely redirect to next page or dashboard (prevent open redirect)
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            # Record failed login attempt for lockout
            if user:
                user.record_failed_login()
                db.session.commit()
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@rate_limit("5 per minute")
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Verify reCAPTCHA if configured
        if current_app.config.get('RECAPTCHA_SECRET_KEY'):
            from app.utils.recaptcha import verify_recaptcha
            token = request.form.get('g-recaptcha-response')
            success, error = verify_recaptcha(token)
            if not success:
                flash(error or 'Please complete the reCAPTCHA', 'error')
                return render_template('auth/register.html', form=form)
        
        user = User(
            email=form.email.data.lower(),
        )
        user.set_password(form.password.data)
        
        # Generate verification token
        user.verification_token = secrets.token_urlsafe(32)
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        email_sent = send_verification_email_safe(user)
        
        # In development, auto-verify if email not configured
        if current_app.config.get('DEBUG') and not email_sent:
            user.verify_email()
            db.session.commit()
            flash('Account created! (Email auto-verified in dev mode)', 'success')
        else:
            flash('Account created! Please check your email to verify your account.', 'success')
        
        login_user(user)
        return redirect(url_for('profile.edit'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/verify/<token>')
def verify_email(token):
    """Verify email address."""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('main.index'))
    
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        flash('Verification link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.resend_verification'))
    
    user.verify_email()
    db.session.commit()
    
    flash('Email verified successfully!', 'success')
    return redirect(url_for('main.dashboard'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
@login_required
def resend_verification():
    """Resend verification email."""
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Generate new token
    current_user.verification_token = secrets.token_urlsafe(32)
    current_user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    
    # Send verification email
    send_verification_email_safe(current_user)
    
    flash('Verification email sent. Please check your inbox.', 'success')
    return redirect(url_for('auth.verification_pending'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@rate_limit("5 per minute")
def forgot_password():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # Generate reset token
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send reset email
            send_password_reset_email_safe(user)
        
        # Always show success to prevent email enumeration
        flash('If an account exists with that email, you will receive a password reset link.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/verification-pending')
@login_required
def verification_pending():
    """Show verification pending page."""
    if current_user.is_verified:
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/verification_pending.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        flash('Reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        
        flash('Password reset successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

