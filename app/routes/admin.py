"""Admin panel routes."""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.models.match import Match, Like
from app.models.message import Message
from app.models.report import Report, Block

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


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
    
    # Recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_reports = Report.query.order_by(desc(Report.created_at)).limit(5).all()
    
    # Denomination breakdown
    denomination_stats = db.session.query(
        Profile.denomination,
        func.count(Profile.id)
    ).group_by(Profile.denomination).all()
    
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
    
    reports_about = Report.query.filter_by(reported_id=user_id).all()
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
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


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
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


@admin_bp.route('/users/<int:user_id>/toggle-premium', methods=['POST'])
@admin_required
def toggle_user_premium(user_id):
    """Toggle premium status."""
    user = User.query.get_or_404(user_id)
    
    user.is_premium = not user.is_premium
    db.session.commit()
    
    action = "granted" if user.is_premium else "revoked"
    flash(f"Premium status {action} for {user.email}.", "success")
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


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
    
    return redirect(url_for('admin.user_detail', user_id=user_id))


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


@admin_bp.route('/reports')
@admin_required
def reports():
    """View all reports."""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    query = Report.query
    
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    reports = query.order_by(desc(Report.created_at)).paginate(page=page, per_page=20)
    
    return render_template('admin/reports.html', reports=reports, status=status)


@admin_bp.route('/reports/<int:report_id>')
@admin_required
def report_detail(report_id):
    """View report details."""
    report = Report.query.get_or_404(report_id)
    
    # Get recent messages between users if relevant
    match = Match.query.filter(
        ((Match.user1_id == report.reporter_id) & (Match.user2_id == report.reported_id)) |
        ((Match.user1_id == report.reported_id) & (Match.user2_id == report.reporter_id))
    ).first()
    
    messages = []
    if match:
        messages = Message.query.filter_by(match_id=match.id).order_by(desc(Message.created_at)).limit(50).all()
    
    # Get other reports about this user
    other_reports = Report.query.filter_by(reported_id=report.reported_id).filter(Report.id != report_id).all()
    
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
        # Could send warning email here
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


@admin_bp.route('/stats/api')
@admin_required
def stats_api():
    """API endpoint for dashboard charts."""
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
    
    return jsonify({
        'daily_signups': [{'date': str(d[0]), 'count': d[1]} for d in daily_signups],
        'daily_messages': [{'date': str(d[0]), 'count': d[1]} for d in daily_messages],
    })

