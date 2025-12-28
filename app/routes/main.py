"""Main routes - landing page and dashboard."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard after login."""
    # Update last active time
    current_user.update_last_active()
    
    # Check if profile is complete
    if not current_user.profile or not current_user.profile.is_complete:
        return redirect(url_for('profile.edit'))
    
    # Get some stats for dashboard
    from app.models.match import Match, Like
    from app.models.message import Message
    
    matches = Match.get_user_matches(current_user.id)
    matches_count = len(matches)
    
    # Get unread message count
    unread_count = 0
    for match in matches:
        unread_count += match.unread_count(current_user.id)
    
    # Get recent matches (last 5)
    recent_matches = matches[:5]
    
    return render_template('main/dashboard.html',
                          matches_count=matches_count,
                          unread_count=unread_count,
                          recent_matches=recent_matches)


@main_bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html')


@main_bp.route('/terms')
def terms():
    """Terms of service."""
    return render_template('main/terms.html')


@main_bp.route('/privacy')
def privacy():
    """Privacy policy."""
    return render_template('main/privacy.html')


@main_bp.route('/offline')
def offline():
    """Offline fallback page for PWA."""
    return render_template('main/offline.html')

