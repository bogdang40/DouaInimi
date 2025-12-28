"""Discovery and matching routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_, or_, not_
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.models.match import Like, Match
from app.models.report import Block
from app.forms.search import SearchForm

discover_bp = Blueprint('discover', __name__)


def get_potential_matches(user, filters=None, page=1, per_page=20):
    """Get potential matches for a user based on preferences and filters.
    
    CONSERVATIVE CHRISTIAN MATCHING:
    - Women only see men
    - Men only see women
    No same-sex matching option.
    """
    profile = user.profile
    if not profile:
        return []
    
    # Base query - users with complete profiles
    query = User.query.join(Profile).filter(
        User.id != user.id,
        User.is_active == True,
        User.is_verified == True,
        Profile.first_name.isnot(None),
        Profile.bio.isnot(None),
    )
    
    # Exclude blocked users (both directions)
    blocked_ids = Block.get_blocked_ids(user.id)
    blocker_ids = Block.get_blocker_ids(user.id)
    excluded_ids = set(blocked_ids + blocker_ids)
    
    # Exclude users already liked
    liked_ids = [like.liked_id for like in user.likes_sent]
    excluded_ids.update(liked_ids)
    
    if excluded_ids:
        query = query.filter(not_(User.id.in_(excluded_ids)))
    
    # CONSERVATIVE MATCHING: Opposite gender only
    # Women see men, men see women
    if profile.gender == 'female':
        query = query.filter(Profile.gender == 'male')
    elif profile.gender == 'male':
        query = query.filter(Profile.gender == 'female')
    else:
        # If gender not set, default to showing opposite (assume user sets their gender)
        pass
    
    # Age range filter
    from datetime import date, timedelta
    today = date.today()
    
    if profile.looking_for_age_min:
        max_birth_date = date(today.year - profile.looking_for_age_min, today.month, today.day)
        query = query.filter(Profile.date_of_birth <= max_birth_date)
    
    if profile.looking_for_age_max:
        min_birth_date = date(today.year - profile.looking_for_age_max - 1, today.month, today.day)
        query = query.filter(Profile.date_of_birth >= min_birth_date)
    
    # Apply additional filters from search form
    if filters:
        if filters.get('denomination'):
            query = query.filter(Profile.denomination == filters['denomination'])
        
        if filters.get('country'):
            query = query.filter(Profile.country == filters['country'])
        
        if filters.get('state_province'):
            query = query.filter(Profile.state_province == filters['state_province'])
        
        if filters.get('speaks_romanian'):
            query = query.filter(Profile.speaks_romanian == filters['speaks_romanian'])
        
        if filters.get('church_attendance'):
            query = query.filter(Profile.church_attendance == filters['church_attendance'])
        
        if filters.get('relationship_goal'):
            query = query.filter(Profile.relationship_goal == filters['relationship_goal'])
    
    # Order by last active (most active first)
    query = query.order_by(User.last_active.desc())
    
    # Paginate
    return query.paginate(page=page, per_page=per_page, error_out=False)


@discover_bp.route('/')
@login_required
def browse():
    """Browse potential matches (grid view)."""
    if not current_user.profile or not current_user.profile.is_complete:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile.edit'))
    
    page = request.args.get('page', 1, type=int)
    matches = get_potential_matches(current_user, page=page)
    
    return render_template('discover/browse.html', 
                          users=matches,
                          page=page)


@discover_bp.route('/swipe')
@login_required
def swipe():
    """Swipe-style discover (Tinder-like)."""
    if not current_user.profile or not current_user.profile.is_complete:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile.edit'))
    
    # Get more users for swipe mode (no pagination needed)
    matches = get_potential_matches(current_user, page=1, per_page=20)
    
    # Get super likes remaining
    is_premium = getattr(current_user, 'is_premium', False)
    super_likes_remaining = Like.super_likes_remaining(current_user.id, is_premium)
    
    return render_template('discover/swipe.html', 
                          users=matches.items if matches else [],
                          super_likes_remaining=super_likes_remaining)


@discover_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search with filters."""
    if not current_user.profile:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile.edit'))
    
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    
    filters = {}
    if request.method == 'POST' and form.validate():
        filters = {
            'denomination': form.denomination.data,
            'country': form.country.data,
            'state_province': form.state_province.data,
            'speaks_romanian': form.speaks_romanian.data,
            'church_attendance': form.church_attendance.data,
            'relationship_goal': form.relationship_goal.data,
        }
        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}
    
    matches = get_potential_matches(current_user, filters=filters, page=page)
    
    return render_template('discover/search.html', 
                          form=form,
                          users=matches,
                          page=page)


@discover_bp.route('/like/<int:user_id>', methods=['POST'])
@login_required
def like_user(user_id):
    """Like a user."""
    is_swipe_mode = request.form.get('swipe_mode') == 'true'
    
    if user_id == current_user.id:
        if is_swipe_mode:
            return jsonify({'error': 'Cannot like yourself'}), 400
        flash('You cannot like yourself.', 'error')
        return redirect(url_for('discover.browse'))
    
    target_user = User.query.get_or_404(user_id)
    
    # Check if blocked
    if current_user.has_blocked(target_user) or current_user.is_blocked_by(target_user):
        if is_swipe_mode:
            return jsonify({'error': 'Cannot interact with this user'}), 403
        flash('Cannot interact with this user.', 'error')
        return redirect(url_for('discover.browse'))
    
    # Create like and check for match
    like, is_match = Like.create_like(current_user.id, user_id)
    
    # For swipe mode, return JSON
    if is_swipe_mode:
        response = {'success': True, 'is_match': is_match}
        if is_match:
            match = Match.query.filter(
                or_(
                    and_(Match.user1_id == current_user.id, Match.user2_id == user_id),
                    and_(Match.user1_id == user_id, Match.user2_id == current_user.id)
                )
            ).first()
            response['matched_user_name'] = target_user.display_name
            response['match_id'] = match.id if match else None
        return jsonify(response)
    
    # For regular mode, redirect
    if is_match:
        flash(f"It's a match! You and {target_user.display_name} have liked each other!", 'success')
        return redirect(url_for('matches.list'))
    else:
        flash(f'You liked {target_user.display_name}!', 'success')
    
    next_url = request.referrer or url_for('discover.browse')
    return redirect(next_url)


@discover_bp.route('/pass/<int:user_id>', methods=['POST'])
@login_required
def pass_user(user_id):
    """Pass on a user (don't show again for now)."""
    is_swipe_mode = request.form.get('swipe_mode') == 'true'
    
    # For now, we just don't create a like - they won't show up again
    # In a more advanced system, we'd track "passes" separately
    
    if is_swipe_mode:
        return jsonify({'success': True, 'is_match': False})
    
    next_url = request.referrer or url_for('discover.browse')
    return redirect(next_url)


@discover_bp.route('/unlike/<int:user_id>', methods=['POST'])
@login_required
def unlike_user(user_id):
    """Remove a like (before matching)."""
    like = Like.query.filter_by(liker_id=current_user.id, liked_id=user_id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        flash('Like removed.', 'info')
    
    return redirect(request.referrer or url_for('discover.browse'))


@discover_bp.route('/super-like/<int:user_id>', methods=['POST'])
@login_required
def super_like_user(user_id):
    """Super like a user (limited per day)."""
    is_swipe_mode = request.form.get('swipe_mode') == 'true'
    
    if user_id == current_user.id:
        if is_swipe_mode:
            return jsonify({'error': 'Cannot super like yourself'}), 400
        flash('You cannot super like yourself.', 'error')
        return redirect(url_for('discover.browse'))
    
    # Check if user can super like
    is_premium = getattr(current_user, 'is_premium', False)
    if not Like.can_super_like(current_user.id, is_premium):
        remaining = Like.super_likes_remaining(current_user.id, is_premium)
        if is_swipe_mode:
            return jsonify({
                'error': 'No super likes remaining today',
                'remaining': remaining
            }), 429
        flash('You have used all your super likes for today. Try again tomorrow!', 'warning')
        return redirect(url_for('discover.browse'))
    
    target_user = User.query.get_or_404(user_id)
    
    # Check if blocked
    if current_user.has_blocked(target_user) or current_user.is_blocked_by(target_user):
        if is_swipe_mode:
            return jsonify({'error': 'Cannot interact with this user'}), 403
        flash('Cannot interact with this user.', 'error')
        return redirect(url_for('discover.browse'))
    
    # Create super like and check for match
    like, is_match = Like.create_like(current_user.id, user_id, is_super=True)
    remaining = Like.super_likes_remaining(current_user.id, is_premium)
    
    # For swipe mode, return JSON
    if is_swipe_mode:
        response = {
            'success': True, 
            'is_match': is_match,
            'is_super': True,
            'super_likes_remaining': remaining
        }
        if is_match:
            match = Match.query.filter(
                or_(
                    and_(Match.user1_id == current_user.id, Match.user2_id == user_id),
                    and_(Match.user1_id == user_id, Match.user2_id == current_user.id)
                )
            ).first()
            response['matched_user_name'] = target_user.display_name
            response['match_id'] = match.id if match else None
        return jsonify(response)
    
    # For regular mode, redirect
    if is_match:
        flash(f"⭐ Super Match! You and {target_user.display_name} have matched!", 'success')
        return redirect(url_for('matches.list'))
    else:
        flash(f'⭐ You super liked {target_user.display_name}! ({remaining} remaining today)', 'success')
    
    next_url = request.referrer or url_for('discover.browse')
    return redirect(next_url)


@discover_bp.route('/super-likes-remaining')
@login_required
def super_likes_remaining():
    """Get remaining super likes for today (API endpoint)."""
    is_premium = getattr(current_user, 'is_premium', False)
    remaining = Like.super_likes_remaining(current_user.id, is_premium)
    limit = Like.PREMIUM_SUPER_LIKES_PER_DAY if is_premium else Like.SUPER_LIKES_PER_DAY
    
    return jsonify({
        'remaining': remaining,
        'limit': limit,
        'is_premium': is_premium
    })

