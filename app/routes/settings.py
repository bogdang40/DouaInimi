"""Settings routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from app.extensions import db
from app.models.report import Block
from app.forms.auth import ChangePasswordForm, ChangeEmailForm
from app.forms.profile import PreferencesForm
from app.services.email import send_email
import secrets

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
def index():
    """Settings overview."""
    return render_template('settings/index.html')


@settings_bp.route('/account')
@login_required
def account():
    """Account settings."""
    return render_template('settings/account.html')


@settings_bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('settings/password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Password changed successfully.', 'success')
        return redirect(url_for('settings.account'))
    
    return render_template('settings/password.html', form=form)


@settings_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Match preferences."""
    if not current_user.profile:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile.edit'))
    
    form = PreferencesForm()
    profile = current_user.profile
    
    if form.validate_on_submit():
        # looking_for_gender is auto-set based on user's gender (opposite sex only)
        # Conservative Christian platform - women see men, men see women
        if profile.gender == 'female':
            profile.looking_for_gender = 'male'
        elif profile.gender == 'male':
            profile.looking_for_gender = 'female'
        
        profile.looking_for_age_min = form.looking_for_age_min.data
        profile.looking_for_age_max = form.looking_for_age_max.data
        profile.relationship_goal = form.relationship_goal.data or None
        
        db.session.commit()
        flash('Preferences updated.', 'success')
        return redirect(url_for('settings.preferences'))
    
    elif request.method == 'GET':
        form.looking_for_age_min.data = profile.looking_for_age_min or 18
        form.looking_for_age_max.data = profile.looking_for_age_max or 99
        form.relationship_goal.data = profile.relationship_goal
    
    return render_template('settings/preferences.html', form=form)


@settings_bp.route('/blocked')
@login_required
def blocked():
    """View blocked users."""
    blocked_users = []
    blocks = Block.query.filter_by(blocker_id=current_user.id).all()
    
    for block in blocks:
        from app.models.user import User
        user = User.query.get(block.blocked_id)
        if user:
            blocked_users.append({
                'user': user,
                'blocked_at': block.created_at
            })
    
    return render_template('settings/blocked.html', blocked_users=blocked_users)


@settings_bp.route('/notifications')
@login_required
def notifications():
    """Notification settings."""
    return render_template('settings/notifications.html')


@settings_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Permanently delete account and all user data (GDPR compliant)."""
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_text = request.form.get('confirm_text', '')

        if not current_user.check_password(password):
            flash('Incorrect password.', 'error')
            return render_template('settings/delete_account.html')

        if confirm_text.lower() != 'delete my account':
            flash('Please type "delete my account" to confirm.', 'error')
            return render_template('settings/delete_account.html')

        # Store user info before deletion for logging
        user_id = current_user.id
        user_email = current_user.email

        try:
            # Delete photos from cloud storage
            from app.utils.storage import delete_photo_from_storage
            from app.models.photo import Photo

            user_photos = Photo.query.filter_by(user_id=user_id).all()
            for photo in user_photos:
                try:
                    delete_photo_from_storage(photo.url)
                    if photo.thumbnail_url:
                        delete_photo_from_storage(photo.thumbnail_url)
                except Exception as e:
                    current_app.logger.warning(f"Failed to delete photo from storage: {e}")

            # Delete all related data (cascade should handle most, but be explicit)
            from app.models.match import Match, Like
            from app.models.message import Message
            from app.models.report import Report

            # Delete messages where user is sender
            Message.query.filter_by(sender_id=user_id).delete()

            # Delete likes made by user
            Like.query.filter_by(liker_id=user_id).delete()
            Like.query.filter_by(liked_id=user_id).delete()

            # Deactivate matches (don't delete - other user's data)
            matches = Match.query.filter(
                (Match.user1_id == user_id) | (Match.user2_id == user_id)
            ).all()
            for match in matches:
                match.is_active = False

            # Delete reports made by user (keep reports about user for safety)
            Report.query.filter_by(reporter_id=user_id).delete()

            # Delete blocks made by and against user
            Block.query.filter_by(blocker_id=user_id).delete()
            Block.query.filter_by(blocked_id=user_id).delete()

            # Now delete the user (cascades to profile and photos)
            from app.models.user import User
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()

            current_app.logger.info(f"User account deleted: {user_email} (ID: {user_id})")

            logout_user()
            flash('Your account and all data have been permanently deleted.', 'info')
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting user account: {e}")
            flash('An error occurred while deleting your account. Please try again.', 'error')
            return render_template('settings/delete_account.html')

    return render_template('settings/delete_account.html')


@settings_bp.route('/export-data')
@login_required
def export_data():
    """Export all user data (GDPR data portability)."""
    import json
    from datetime import datetime
    from flask import Response
    from app.models.match import Match, Like
    from app.models.message import Message

    user_data = {
        'exported_at': datetime.utcnow().isoformat(),
        'account': {
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'is_verified': current_user.is_verified,
            'is_premium': current_user.is_premium,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
        },
        'profile': {},
        'photos': [],
        'matches': [],
        'messages_sent': [],
        'likes_sent': [],
    }

    # Profile data
    if current_user.profile:
        p = current_user.profile
        user_data['profile'] = {
            'first_name': p.first_name,
            'last_name': p.last_name,
            'date_of_birth': p.date_of_birth.isoformat() if p.date_of_birth else None,
            'gender': p.gender,
            'city': p.city,
            'state_province': p.state_province,
            'country': p.country,
            'bio': p.bio,
            'denomination': p.denomination,
            'occupation': p.occupation,
            'education': p.education,
        }

    # Photos (URLs only)
    for photo in current_user.photos:
        user_data['photos'].append({
            'filename': photo.filename,
            'is_primary': photo.is_primary,
            'created_at': photo.created_at.isoformat() if photo.created_at else None,
        })

    # Matches
    matches = Match.query.filter(
        (Match.user1_id == current_user.id) | (Match.user2_id == current_user.id)
    ).all()
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        user_data['matches'].append({
            'matched_with': other_user.display_name if other_user else 'Deleted User',
            'matched_at': match.matched_at.isoformat() if match.matched_at else None,
            'is_active': match.is_active,
        })

    # Messages sent
    messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at).all()
    for msg in messages:
        user_data['messages_sent'].append({
            'content': msg.content,
            'created_at': msg.created_at.isoformat() if msg.created_at else None,
        })

    # Likes sent
    likes = Like.query.filter_by(liker_id=current_user.id).all()
    for like in likes:
        from app.models.user import User
        liked_user = User.query.get(like.liked_id)
        user_data['likes_sent'].append({
            'liked_user': liked_user.display_name if liked_user else 'Deleted User',
            'created_at': like.created_at.isoformat() if like.created_at else None,
            'is_super_like': like.is_super_like,
        })

    # Return as downloadable JSON
    response = Response(
        json.dumps(user_data, indent=2, ensure_ascii=False),
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=my_data_{datetime.utcnow().strftime("%Y%m%d")}.json'}
    )
    return response


@settings_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate():
    """Temporarily deactivate account."""
    current_user.is_active = False
    db.session.commit()
    
    logout_user()
    flash('Your account has been deactivated. You can reactivate by logging in again.', 'info')
    return redirect(url_for('main.index'))


@settings_bp.route('/email', methods=['GET', 'POST'])
@login_required
def change_email():
    """Change email address."""
    if request.method == 'POST':
        new_email = request.form.get('new_email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not current_user.check_password(password):
            flash('Incorrect password.', 'error')
            return render_template('settings/change_email.html')
        
        if not new_email or '@' not in new_email:
            flash('Please enter a valid email address.', 'error')
            return render_template('settings/change_email.html')
        
        # Check if email is already taken
        from app.models.user import User
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != current_user.id:
            flash('This email is already in use.', 'error')
            return render_template('settings/change_email.html')
        
        # Update email and require re-verification
        current_user.email = new_email
        current_user.is_verified = False
        current_user.verification_token = secrets.token_urlsafe(32)
        db.session.commit()
        
        # Send verification email
        try:
            from flask import current_app
            verify_url = url_for('auth.verify_email', token=current_user.verification_token, _external=True)
            send_email(
                to=new_email,
                subject=f'Verify Your New Email - {current_app.config["APP_NAME"]}',
                template='emails/verify_email.html',
                verify_url=verify_url
            )
        except Exception as e:
            print(f"Email send error: {e}")
        
        flash('Email updated! Please check your new email for verification.', 'success')
        return redirect(url_for('settings.index'))
    
    return render_template('settings/change_email.html')


@settings_bp.route('/verify-account')
@login_required
def verify_account():
    """Resend verification email."""
    if current_user.is_verified:
        flash('Your account is already verified.', 'info')
        return redirect(url_for('settings.index'))
    
    # Generate new token
    current_user.verification_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    try:
        from flask import current_app
        verify_url = url_for('auth.verify_email', token=current_user.verification_token, _external=True)
        send_email(
            to=current_user.email,
            subject=f'Verify Your Email - {current_app.config["APP_NAME"]}',
            template='emails/verify_email.html',
            verify_url=verify_url
        )
        flash('Verification email sent! Check your inbox.', 'success')
    except Exception as e:
        print(f"Email send error: {e}")
        flash('Could not send verification email. Please try again later.', 'error')
    
    return redirect(url_for('settings.index'))


@settings_bp.route('/privacy', methods=['POST'])
@login_required
def update_privacy():
    """Update privacy settings."""
    current_user.show_online = 'show_online' in request.form
    current_user.show_distance = 'show_distance' in request.form
    db.session.commit()
    
    flash('Privacy settings updated.', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/notifications', methods=['POST'])
@login_required
def update_notifications():
    """Update notification settings."""
    current_user.notify_matches = 'notify_matches' in request.form
    current_user.notify_messages = 'notify_messages' in request.form
    db.session.commit()
    
    flash('Notification settings updated.', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/pause', methods=['GET', 'POST'])
@login_required
def pause_account():
    """Pause/unpause account (hide from search)."""
    if request.method == 'POST':
        current_user.is_paused = not current_user.is_paused
        db.session.commit()
        
        if current_user.is_paused:
            flash('Your account is now paused. You won\'t appear in searches.', 'info')
        else:
            flash('Your account is now active again!', 'success')
        
        return redirect(url_for('settings.index'))
    
    return render_template('settings/pause_account.html')

