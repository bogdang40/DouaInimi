"""Safety routes for reporting and blocking users."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.report import Report, Block
from app.models.match import Match

safety_bp = Blueprint('safety', __name__)


# Report reasons
REPORT_REASONS = [
    ('fake_profile', 'Fake Profile'),
    ('inappropriate_photos', 'Inappropriate Photos'),
    ('inappropriate_content', 'Inappropriate Content/Bio'),
    ('harassment', 'Harassment or Threatening Behavior'),
    ('spam', 'Spam or Scam'),
    ('underage', 'Appears to be Underage'),
    ('impersonation', 'Impersonating Someone'),
    ('other', 'Other'),
]


@safety_bp.route('/report/<int:user_id>', methods=['GET', 'POST'])
@login_required
def report_user(user_id):
    """Report a user."""
    if user_id == current_user.id:
        flash("You cannot report yourself.", "error")
        return redirect(url_for('main.dashboard'))
    
    reported_user = User.query.get_or_404(user_id)
    
    # Check if already reported recently
    existing_report = Report.query.filter_by(
        reporter_id=current_user.id,
        reported_id=user_id,
        status='pending'
    ).first()
    
    if existing_report:
        flash("You have already reported this user. We're reviewing it.", "info")
        return redirect(url_for('profile.view_user', user_id=user_id))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        description = request.form.get('description', '').strip()
        
        if not reason or reason not in [r[0] for r in REPORT_REASONS]:
            flash("Please select a valid reason.", "error")
            return render_template('safety/report.html', 
                                   user=reported_user, 
                                   reasons=REPORT_REASONS)
        
        # Create report
        report = Report(
            reporter_id=current_user.id,
            reported_id=user_id,
            reason=reason,
            description=description
        )
        db.session.add(report)
        db.session.commit()
        
        flash("Thank you for your report. Our team will review it shortly.", "success")
        
        # Optionally also block the user
        if request.form.get('also_block'):
            Block.block_user(current_user.id, user_id)
            flash(f"You've also blocked {reported_user.display_name}.", "info")
        
        return redirect(url_for('discover.browse'))
    
    return render_template('safety/report.html', 
                           user=reported_user, 
                           reasons=REPORT_REASONS)


@safety_bp.route('/block/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    """Block a user."""
    if user_id == current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Cannot block yourself'}), 400
        flash("You cannot block yourself.", "error")
        return redirect(url_for('main.dashboard'))
    
    blocked_user = User.query.get_or_404(user_id)
    
    # Check if already blocked
    if current_user.has_blocked(blocked_user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'already_blocked'})
        flash(f"{blocked_user.display_name} is already blocked.", "info")
        return redirect(request.referrer or url_for('discover.browse'))
    
    # Block the user
    Block.block_user(current_user.id, user_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'blocked', 'message': f'{blocked_user.display_name} has been blocked'})
    
    flash(f"{blocked_user.display_name} has been blocked. You won't see each other anymore.", "success")
    return redirect(url_for('discover.browse'))


@safety_bp.route('/unblock/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    """Unblock a user."""
    blocked_user = User.query.get_or_404(user_id)
    
    if not current_user.has_blocked(blocked_user):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'User is not blocked'}), 400
        flash(f"{blocked_user.display_name} is not blocked.", "info")
        return redirect(request.referrer or url_for('settings.blocked_users'))
    
    Block.unblock_user(current_user.id, user_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'unblocked', 'message': f'{blocked_user.display_name} has been unblocked'})
    
    flash(f"{blocked_user.display_name} has been unblocked.", "success")
    return redirect(request.referrer or url_for('settings.blocked_users'))


@safety_bp.route('/blocked')
@login_required
def blocked_users():
    """View list of blocked users."""
    blocked_ids = Block.get_blocked_ids(current_user.id)
    blocked = User.query.filter(User.id.in_(blocked_ids)).all() if blocked_ids else []
    
    return render_template('safety/blocked.html', blocked_users=blocked)

