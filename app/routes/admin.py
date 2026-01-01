"""Admin panel routes - Full user management and approval system."""
import os
import hashlib
import secrets
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, session, current_app
from flask_login import current_user
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.profile import Profile
from app.models.match import Match, Like
from app.models.message import Message
from app.models.report import Report, Block

admin_bp = Blueprint('admin', __name__)


def get_admin_credentials():
    """Get admin credentials from environment variables.

    Set these in Azure App Service Configuration:
    - ADMIN_EMAIL: admin email address
    - ADMIN_PASSWORD_HASH: bcrypt hash of admin password

    To generate a password hash, run:
        python -c "from flask_bcrypt import Bcrypt; b = Bcrypt(); print(b.generate_password_hash('your_password').decode())"
    """
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')

    if not admin_email or not admin_password_hash:
        current_app.logger.warning("ADMIN_EMAIL or ADMIN_PASSWORD_HASH not set in environment")
        return None, None

    return admin_email.lower(), admin_password_hash


def verify_admin_password(password):
    """Verify admin password against stored hash."""
    _, password_hash = get_admin_credentials()
    if not password_hash:
        return False
    try:
        return bcrypt.check_password_hash(password_hash, password)
    except Exception:
        return False


def admin_required(f):
    """Decorator to require admin access via session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin_authenticated'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== ADMIN LOGIN ==========

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Separate admin login page with secure credential verification."""
    # Already logged in as admin?
    if session.get('is_admin_authenticated'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        admin_email, _ = get_admin_credentials()

        # Check credentials securely
        if admin_email and email == admin_email and verify_admin_password(password):
            session['is_admin_authenticated'] = True
            session['admin_email'] = email
            session.permanent = True  # Use permanent session for admin
            current_app.logger.info(f"Admin login successful: {email}")
            flash('Welcome to the Admin Panel!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            current_app.logger.warning(f"Failed admin login attempt: {email}")
            flash('Invalid admin credentials.', 'error')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def admin_logout():
    """Logout from admin panel."""
    session.pop('is_admin_authenticated', None)
    session.pop('admin_email', None)
    flash('Logged out from admin panel.', 'success')
    return redirect(url_for('admin.admin_login'))


@admin_bp.context_processor
def inject_admin_counts():
    """Inject admin counts into all admin templates.

    Optimized: Uses a single query with subqueries instead of 3 separate COUNT queries.
    """
    if session.get('is_admin_authenticated'):
        from app.models.photo import Photo

        # Single query with multiple subqueries - more efficient than 3 separate queries
        result = db.session.query(
            db.session.query(func.count(User.id))
                .filter(User.is_approved == False, User.is_active == True)
                .scalar_subquery().label('pending_approvals'),
            db.session.query(func.count(Report.id))
                .filter(Report.status == 'pending')
                .scalar_subquery().label('pending_reports'),
            db.session.query(func.count(Photo.id))
                .filter(Photo.moderation_status == 'pending')
                .scalar_subquery().label('pending_photos')
        ).first()

        return {
            'pending_approval_count': result[0] or 0,
            'pending_reports_count': result[1] or 0,
            'pending_photos_count': result[2] or 0,
            'now': datetime.utcnow
        }
    return {'now': datetime.utcnow}


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with overview stats."""
    # User stats
    total_users = User.query.count()
    new_users_today = User.query.filter(
        User.created_at >= datetime.utcnow().date()
    ).count()
    new_users_week = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    verified_users = User.query.filter_by(is_verified=True).count()
    active_users = User.query.filter(
        User.last_active >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    pending_approvals = User.query.filter_by(is_approved=False, is_active=True).count()
    
    # Match & message stats
    total_matches = Match.query.filter_by(is_active=True).count()
    new_matches_today = Match.query.filter(
        Match.matched_at >= datetime.utcnow().date()
    ).count()
    total_messages = Message.query.count()
    messages_today = Message.query.filter(
        Message.created_at >= datetime.utcnow().date()
    ).count()
    
    # Report stats
    pending_reports = Report.query.filter_by(status='pending').count()
    
    # Recent activity (eager load relationships to avoid N+1 queries)
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_reports = Report.query.options(
        joinedload(Report.reporter),
        joinedload(Report.reported)
    ).order_by(desc(Report.created_at)).limit(5).all()
    
    # Denomination breakdown
    denomination_stats = db.session.query(
        Profile.denomination,
        func.count(Profile.id)
    ).group_by(Profile.denomination).order_by(desc(func.count(Profile.id))).all()
    
    # Gender breakdown
    gender_stats = db.session.query(
        Profile.gender,
        func.count(Profile.id)
    ).group_by(Profile.gender).all()
    
    return render_template('admin/dashboard.html',
        total_users=total_users,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        verified_users=verified_users,
        active_users=active_users,
        pending_approvals=pending_approvals,
        total_matches=total_matches,
        new_matches_today=new_matches_today,
        total_messages=total_messages,
        messages_today=messages_today,
        pending_reports=pending_reports,
        recent_users=recent_users,
        recent_reports=recent_reports,
        denomination_stats=denomination_stats,
        gender_stats=gender_stats
    )


# ========== APPROVALS ==========

@admin_bp.route('/approvals')
@admin_required
def approvals():
    """User approval page."""
    pending_users = User.query.filter_by(is_approved=False, is_active=True)\
        .order_by(User.created_at.asc()).all()
    
    stats = {
        'pending': len(pending_users),
        'approved': User.query.filter_by(is_approved=True).count(),
        'rejected': 0  # We delete rejected users, so this is always 0
    }
    
    return render_template('admin/approvals.html', 
                          pending_users=pending_users, 
                          stats=stats)


@admin_bp.route('/approvals/<int:user_id>/approve', methods=['POST'])
@admin_required
def approve_user(user_id):
    """Approve a user registration."""
    user = User.query.get_or_404(user_id)
    
    user.is_approved = True
    db.session.commit()
    
    flash(f"User {user.email} has been approved!", "success")
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/approvals/<int:user_id>/reject', methods=['POST'])
@admin_required
def reject_user(user_id):
    """Reject and delete a user registration."""
    user = User.query.get_or_404(user_id)
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User {email} has been rejected and deleted.", "success")
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/approvals/approve-all', methods=['POST'])
@admin_required
def approve_all():
    """Approve all pending users."""
    pending_users = User.query.filter_by(is_approved=False, is_active=True).all()
    count = len(pending_users)
    
    for user in pending_users:
        user.is_approved = True
    
    db.session.commit()
    
    flash(f"Approved {count} users!", "success")
    return redirect(url_for('admin.approvals'))


# ========== USERS ==========

@admin_bp.route('/users')
@admin_required
def users():
    """User management page."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    status = request.args.get('status', '')
    
    query = User.query
    
    if search:
        query = query.filter(User.email.ilike(f'%{search}%'))
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    elif status == 'verified':
        query = query.filter_by(is_verified=True)
    elif status == 'unverified':
        query = query.filter_by(is_verified=False)
    elif status == 'premium':
        query = query.filter_by(is_premium=True)
    elif status == 'admin':
        query = query.filter_by(is_admin=True)
    
    users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=20)
    
    return render_template('admin/users.html', 
                          users=users, 
                          search=search, 
                          status=status)


@admin_bp.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """View user details."""
    user = User.query.get_or_404(user_id)

    # Get user's activity stats
    matches_count = Match.query.filter(
        (Match.user1_id == user_id) | (Match.user2_id == user_id)
    ).count()

    messages_sent = Message.query.filter_by(sender_id=user_id).count()

    # Eager load reporter to avoid N+1 queries
    reports_about = Report.query.options(
        joinedload(Report.reporter)
    ).filter_by(reported_id=user_id).all()
    reports_made = Report.query.filter_by(reporter_id=user_id).count()

    return render_template('admin/user_detail.html',
        user=user,
        matches_count=matches_count,
        messages_sent=messages_sent,
        reports_about=reports_about,
        reports_made=reports_made
    )


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Suspend or reactivate a user."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot suspend yourself.", "error")
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    action = "reactivated" if user.is_active else "suspended"
    flash(f"User {user.email} has been {action}.", "success")
    
    return redirect(request.referrer or url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle-verified', methods=['POST'])
@admin_required
def toggle_user_verified(user_id):
    """Manually verify or unverify a user."""
    user = User.query.get_or_404(user_id)
    
    user.is_verified = not user.is_verified
    if user.is_verified:
        user.email_verified_at = datetime.utcnow()
    else:
        user.email_verified_at = None
    
    db.session.commit()
    
    action = "verified" if user.is_verified else "unverified"
    flash(f"User {user.email} has been {action}.", "success")
    
    return redirect(request.referrer or url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle-premium', methods=['POST'])
@admin_required
def toggle_user_premium(user_id):
    """Toggle premium status."""
    user = User.query.get_or_404(user_id)
    
    user.is_premium = not user.is_premium
    db.session.commit()
    
    action = "granted" if user.is_premium else "revoked"
    flash(f"Premium status {action} for {user.email}.", "success")
    
    return redirect(request.referrer or url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_user_admin(user_id):
    """Toggle admin status."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot modify your own admin status.", "error")
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "granted" if user.is_admin else "revoked"
    flash(f"Admin status {action} for {user.email}.", "success")
    
    return redirect(request.referrer or url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Permanently delete a user."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot delete yourself.", "error")
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User {email} has been permanently deleted.", "success")
    return redirect(url_for('admin.users'))


# ========== REPORTS ==========

@admin_bp.route('/reports')
@admin_required
def reports():
    """View all reports."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')

    # Eager load reporter and reported to avoid N+1 queries
    query = Report.query.options(
        joinedload(Report.reporter),
        joinedload(Report.reported)
    )

    if status and status != 'all':
        query = query.filter_by(status=status)

    reports = query.order_by(desc(Report.created_at)).paginate(page=page, per_page=20)

    return render_template('admin/reports.html', reports=reports, status=status)


@admin_bp.route('/reports/<int:report_id>')
@admin_required
def report_detail(report_id):
    """View report details."""
    # Eager load reporter and reported to avoid N+1 queries
    report = Report.query.options(
        joinedload(Report.reporter),
        joinedload(Report.reported)
    ).get_or_404(report_id)

    # Get recent messages between users if relevant
    match = Match.query.filter(
        ((Match.user1_id == report.reporter_id) & (Match.user2_id == report.reported_id)) |
        ((Match.user1_id == report.reported_id) & (Match.user2_id == report.reporter_id))
    ).first()

    messages = []
    if match:
        # Eager load sender to avoid N+1 queries when displaying messages
        messages = Message.query.options(
            joinedload(Message.sender)
        ).filter_by(match_id=match.id).order_by(desc(Message.created_at)).limit(50).all()

    # Get other reports about this user with eager loading
    other_reports = Report.query.options(
        joinedload(Report.reporter)
    ).filter_by(reported_id=report.reported_id).filter(Report.id != report_id).all()

    return render_template('admin/report_detail.html',
        report=report,
        messages=messages,
        other_reports=other_reports
    )


@admin_bp.route('/reports/<int:report_id>/resolve', methods=['POST'])
@admin_required
def resolve_report(report_id):
    """Resolve a report."""
    report = Report.query.get_or_404(report_id)
    
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    if action == 'dismiss':
        report.status = 'dismissed'
        report.resolution_notes = notes
        report.resolved_by_id = current_user.id
        report.resolved_at = datetime.utcnow()
        flash("Report dismissed.", "success")
    
    elif action == 'warn':
        report.status = 'resolved'
        report.resolution_notes = f"Warning issued. {notes}"
        report.resolved_by_id = current_user.id
        report.resolved_at = datetime.utcnow()
        flash("Warning issued to user.", "success")
    
    elif action == 'suspend':
        report.status = 'resolved'
        report.resolution_notes = f"User suspended. {notes}"
        report.resolved_by_id = current_user.id
        report.resolved_at = datetime.utcnow()
        
        # Suspend the reported user
        reported_user = User.query.get(report.reported_id)
        if reported_user:
            reported_user.is_active = False
        
        flash("User has been suspended.", "success")
    
    elif action == 'ban':
        report.status = 'resolved'
        report.resolution_notes = f"User banned and deleted. {notes}"
        report.resolved_by_id = current_user.id
        report.resolved_at = datetime.utcnow()
        
        # Delete the reported user
        reported_user = User.query.get(report.reported_id)
        if reported_user:
            db.session.delete(reported_user)
        
        flash("User has been banned and deleted.", "success")
    
    db.session.commit()
    
    return redirect(url_for('admin.reports'))


# ========== FLAGGED CONTENT ==========

@admin_bp.route('/flagged')
@admin_required
def flagged_content():
    """View flagged content that needs review.
    
    Shows profiles that have been reported multiple times.
    """
    from sqlalchemy import func
    
    # Step 1: Get user IDs with their report counts (PostgreSQL-compatible)
    subquery = db.session.query(
        Report.reported_id,
        func.count(Report.id).label('report_count')
    ).filter(Report.status == 'pending')\
     .group_by(Report.reported_id)\
     .having(func.count(Report.id) >= 1)\
     .subquery()
    
    # Step 2: Join with users to get full user objects with report counts
    flagged_data = db.session.query(
        User,
        subquery.c.report_count
    ).join(subquery, User.id == subquery.c.reported_id)\
     .order_by(subquery.c.report_count.desc())\
     .all()
    
    return render_template('admin/flagged.html', flagged_users=flagged_data)


@admin_bp.route('/flagged/<int:user_id>/dismiss', methods=['POST'])
@admin_required
def dismiss_flagged(user_id):
    """Dismiss all pending reports for a user."""
    reports = Report.query.filter_by(reported_id=user_id, status='pending').all()
    
    for report in reports:
        report.status = 'dismissed'
        report.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f"Dismissed {len(reports)} reports.", "success")
    return redirect(url_for('admin.flagged_content'))


# ========== ANALYTICS ==========

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics dashboard."""
    # Get daily signups for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_signups = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(User.created_at >= thirty_days_ago)\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at))\
     .all()
    
    # Get daily messages for last 30 days
    daily_messages = db.session.query(
        func.date(Message.created_at),
        func.count(Message.id)
    ).filter(Message.created_at >= thirty_days_ago)\
     .group_by(func.date(Message.created_at))\
     .order_by(func.date(Message.created_at))\
     .all()
    
    # Get daily matches for last 30 days
    daily_matches = db.session.query(
        func.date(Match.matched_at),
        func.count(Match.id)
    ).filter(Match.matched_at >= thirty_days_ago)\
     .group_by(func.date(Match.matched_at))\
     .order_by(func.date(Match.matched_at))\
     .all()
    
    return render_template('admin/analytics.html',
        daily_signups=daily_signups,
        daily_messages=daily_messages,
        daily_matches=daily_matches
    )


# ========== SETTINGS ==========

@admin_bp.route('/settings')
@admin_required
def settings():
    """Admin settings page."""
    return render_template('admin/settings.html')


# ========== API ENDPOINTS ==========

@admin_bp.route('/api/stats')
@admin_required
def stats_api():
    """API endpoint for dashboard charts."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    daily_signups = db.session.query(
        func.date(User.created_at),
        func.count(User.id)
    ).filter(User.created_at >= thirty_days_ago)\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at))\
     .all()
    
    daily_messages = db.session.query(
        func.date(Message.created_at),
        func.count(Message.id)
    ).filter(Message.created_at >= thirty_days_ago)\
     .group_by(func.date(Message.created_at))\
     .order_by(func.date(Message.created_at))\
     .all()
    
    return jsonify({
        'daily_signups': [{'date': str(d[0]), 'count': d[1]} for d in daily_signups],
        'daily_messages': [{'date': str(d[0]), 'count': d[1]} for d in daily_messages],
    })


# ========== PHOTO MODERATION ==========

@admin_bp.route('/photos')
@admin_required
def photos():
    """View photos pending moderation."""
    from app.models.photo import Photo
    from sqlalchemy.orm import joinedload

    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)

    query = Photo.query.options(joinedload(Photo.user))

    if status == 'pending':
        query = query.filter_by(moderation_status='pending')
    elif status == 'approved':
        query = query.filter_by(moderation_status='approved')
    elif status == 'rejected':
        query = query.filter_by(moderation_status='rejected')

    photos = query.order_by(Photo.created_at.desc()).paginate(page=page, per_page=20)

    # Stats
    pending_count = Photo.query.filter_by(moderation_status='pending').count()
    approved_count = Photo.query.filter_by(moderation_status='approved').count()
    rejected_count = Photo.query.filter_by(moderation_status='rejected').count()

    return render_template('admin/photos.html',
        photos=photos,
        status=status,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count
    )


@admin_bp.route('/photos/<int:photo_id>/approve', methods=['POST'])
@admin_required
def approve_photo(photo_id):
    """Approve a photo."""
    from app.models.photo import Photo

    photo = Photo.query.get_or_404(photo_id)
    photo.approve(admin_id=None)  # Admin ID would come from session if we tracked it

    flash(f"Photo approved.", "success")
    return redirect(request.referrer or url_for('admin.photos'))


@admin_bp.route('/photos/<int:photo_id>/reject', methods=['POST'])
@admin_required
def reject_photo(photo_id):
    """Reject a photo."""
    from app.models.photo import Photo

    photo = Photo.query.get_or_404(photo_id)
    notes = request.form.get('notes', 'Photo does not meet guidelines')
    photo.reject(admin_id=None, notes=notes)

    flash(f"Photo rejected.", "success")
    return redirect(request.referrer or url_for('admin.photos'))


@admin_bp.route('/photos/approve-all', methods=['POST'])
@admin_required
def approve_all_photos():
    """Approve all pending photos."""
    from app.models.photo import Photo

    pending = Photo.query.filter_by(moderation_status='pending').all()
    count = len(pending)

    for photo in pending:
        photo.is_approved = True
        photo.moderation_status = 'approved'
        photo.moderated_at = datetime.utcnow()

    db.session.commit()

    flash(f"Approved {count} photos.", "success")
    return redirect(url_for('admin.photos'))
