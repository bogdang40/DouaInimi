"""Match routes."""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.match import Match, Like
from app.models.report import Block, Report
from app.forms.messages import ReportForm

matches_bp = Blueprint('matches', __name__)


@matches_bp.route('/')
@login_required
def list():
    """List all matches - Tinder style.

    OPTIMIZED: Uses get_user_matches_with_details to avoid N+1 queries.
    """
    # Single optimized query gets matches + last message + unread count
    matches = Match.get_user_matches_with_details(current_user.id)

    # Separate new matches (no messages) from conversations
    new_matches = []
    conversations = []

    for match in matches:
        # Use cached data instead of triggering new queries
        if match.get_cached_last_message() is None:
            new_matches.append(match)
        else:
            conversations.append(match)

    # Sort conversations by last message time (most recent first)
    # Using cached time instead of accessing relationship
    conversations.sort(
        key=lambda m: getattr(m, '_cached_last_message_time', None) or m.matched_at,
        reverse=True
    )

    # Get pending likes (people who liked you but you haven't liked back)
    pending_likes = Like.query.filter(
        Like.liked_id == current_user.id,
        ~Like.liker_id.in_(
            db.session.query(Like.liked_id).filter(Like.liker_id == current_user.id)
        )
    ).order_by(Like.created_at.desc()).all()

    return render_template('matches/list.html',
                          matches=conversations,
                          new_matches=new_matches,
                          pending_likes=pending_likes,
                          now=datetime.utcnow())


@matches_bp.route('/<int:match_id>/unmatch', methods=['POST'])
@login_required
def unmatch(match_id):
    """Unmatch with a user."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        flash('Invalid match.', 'error')
        return redirect(url_for('matches.list'))
    
    other_user = match.get_other_user(current_user.id)
    match.unmatch(current_user.id)
    
    flash(f'You have unmatched with {other_user.display_name}.', 'info')
    return redirect(url_for('matches.list'))


@matches_bp.route('/block/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    """Block a user."""
    if user_id == current_user.id:
        flash('You cannot block yourself.', 'error')
        return redirect(url_for('matches.list'))
    
    from app.models.user import User
    target_user = User.query.get_or_404(user_id)
    
    Block.block_user(current_user.id, user_id)
    
    flash(f'{target_user.display_name} has been blocked.', 'info')
    return redirect(url_for('matches.list'))


@matches_bp.route('/unblock/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    """Unblock a user."""
    Block.unblock_user(current_user.id, user_id)
    
    flash('User has been unblocked.', 'info')
    return redirect(url_for('settings.blocked'))


@matches_bp.route('/report/<int:user_id>', methods=['GET', 'POST'])
@login_required
def report_user(user_id):
    """Report a user."""
    if user_id == current_user.id:
        flash('You cannot report yourself.', 'error')
        return redirect(url_for('matches.list'))
    
    from app.models.user import User
    target_user = User.query.get_or_404(user_id)
    
    form = ReportForm()
    
    if form.validate_on_submit():
        Report.create_report(
            reporter_id=current_user.id,
            reported_id=user_id,
            reason=form.reason.data,
            details=form.details.data
        )
        
        # Optionally auto-block
        Block.block_user(current_user.id, user_id)
        
        flash('Report submitted. Thank you for helping keep our community safe.', 'success')
        return redirect(url_for('matches.list'))
    
    return render_template('matches/report.html', form=form, user=target_user)


@matches_bp.route('/who-likes-me')
@login_required
def who_likes_me():
    """See who has liked you (premium feature placeholder)."""
    if not current_user.is_premium:
        flash('This is a premium feature.', 'info')
        return redirect(url_for('matches.list'))
    
    # Get users who have liked current user but aren't matched yet
    likes = Like.query.filter_by(liked_id=current_user.id).all()
    likers = []
    
    for like in likes:
        # Check if already matched
        if not current_user.is_matched_with(like.liker):
            likers.append(like.liker)
    
    return render_template('matches/who_likes_me.html', users=likers)

