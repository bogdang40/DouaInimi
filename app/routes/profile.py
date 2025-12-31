"""Profile routes."""
import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.user import User
from app.models.profile import Profile
from app.models.photo import Photo
from app.forms.profile import ProfileForm, PhotoUploadForm
from app.utils.image import process_uploaded_image, validate_image_file
from app.utils.moderation import moderate_profile
from app.utils.storage import upload_photo_to_storage, delete_photo_from_storage, generate_unique_filename

profile_bp = Blueprint('profile', __name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@profile_bp.route('/')
@login_required
def view():
    """View own profile."""
    if not current_user.profile:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile.edit'))
    
    return render_template('profile/view.html', user=current_user, is_own_profile=True)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit own profile."""
    form = ProfileForm()
    
    # If user has no profile, create one
    if not current_user.profile:
        profile = Profile(user_id=current_user.id)
    else:
        profile = current_user.profile
    
    if form.validate_on_submit():
        # Update profile fields
        profile.first_name = form.first_name.data
        profile.last_name = form.last_name.data
        profile.date_of_birth = form.date_of_birth.data
        profile.gender = form.gender.data
        
        profile.city = form.city.data
        profile.state_province = form.state_province.data
        profile.country = form.country.data
        
        profile.romanian_origin_region = form.romanian_origin_region.data or None
        profile.speaks_romanian = form.speaks_romanian.data or None
        profile.years_in_north_america = form.years_in_north_america.data
        
        profile.denomination = form.denomination.data
        profile.church_name = form.church_name.data or None
        profile.church_attendance = form.church_attendance.data or None
        profile.faith_importance = form.faith_importance.data or None
        
        profile.bio = form.bio.data
        profile.occupation = form.occupation.data or None
        profile.education = form.education.data or None
        
        # Handle height - either from cm or ft/in
        if form.height_cm.data:
            profile.height_cm = form.height_cm.data
        elif form.height_ft.data and form.height_in.data:
            # Convert feet/inches to cm
            feet = int(form.height_ft.data) if form.height_ft.data else 0
            inches = int(form.height_in.data) if form.height_in.data else 0
            total_inches = (feet * 12) + inches
            profile.height_cm = int(total_inches * 2.54)
        
        profile.has_children = form.has_children.data
        profile.wants_children = form.wants_children.data or None
        profile.smoking = form.smoking.data or None
        profile.drinking = form.drinking.data or None
        
        # Traditional/Conservative values
        profile.conservatism_level = form.conservatism_level.data or None
        profile.head_covering = form.head_covering.data or None
        profile.fasting_practice = form.fasting_practice.data or None
        profile.prayer_frequency = form.prayer_frequency.data or None
        profile.bible_reading = form.bible_reading.data or None
        profile.dietary_restrictions = form.dietary_restrictions.data or None
        profile.family_role_view = form.family_role_view.data or None
        profile.wants_spouse_same_denomination = form.wants_spouse_same_denomination.data
        profile.willing_to_relocate = form.willing_to_relocate.data
        profile.wants_church_wedding = form.wants_church_wedding.data
        
        # Conservative matching: Auto-set looking_for_gender to opposite gender
        # Women see men, men see women
        if profile.gender == 'female':
            profile.looking_for_gender = 'male'
        elif profile.gender == 'male':
            profile.looking_for_gender = 'female'
        else:
            profile.looking_for_gender = None
        
        profile.looking_for_age_min = form.looking_for_age_min.data or 18
        profile.looking_for_age_max = form.looking_for_age_max.data or 99
        profile.relationship_goal = form.relationship_goal.data or None
        
        if not current_user.profile:
            db.session.add(profile)
        
        db.session.commit()
        
        # Run content moderation if enabled
        if current_app.config.get('ENABLE_AUTO_MODERATION'):
            mod_result = moderate_profile(profile)
            if mod_result.is_flagged:
                current_app.logger.warning(
                    f"Profile {profile.id} flagged: {mod_result.flags}"
                )
                if mod_result.auto_action == 'flag_for_review':
                    # Create a report for admin review
                    from app.utils.moderation import flag_user_for_review
                    flag_user_for_review(
                        current_user, 
                        f"Auto-moderation: {len(mod_result.flags)} flags",
                        mod_result.severity
                    )
        
        flash('Profile updated successfully!', 'success')
        
        # Check if we need to redirect to photo upload
        if not current_user.photos:
            flash('Please upload at least one photo to complete your profile.', 'info')
            return redirect(url_for('profile.photos'))
        
        return redirect(url_for('profile.view'))
    
    # Pre-populate form for GET request
    elif request.method == 'GET' and current_user.profile:
        form.first_name.data = profile.first_name
        form.last_name.data = profile.last_name
        form.date_of_birth.data = profile.date_of_birth
        form.gender.data = profile.gender
        
        form.city.data = profile.city
        form.state_province.data = profile.state_province
        form.country.data = profile.country
        
        form.romanian_origin_region.data = profile.romanian_origin_region
        form.speaks_romanian.data = profile.speaks_romanian
        form.years_in_north_america.data = profile.years_in_north_america
        
        form.denomination.data = profile.denomination
        form.church_name.data = profile.church_name
        form.church_attendance.data = profile.church_attendance
        form.faith_importance.data = profile.faith_importance
        
        form.bio.data = profile.bio
        form.occupation.data = profile.occupation
        form.education.data = profile.education
        form.height_cm.data = profile.height_cm
        
        # Also convert height_cm to ft/in for display
        if profile.height_cm:
            total_inches = profile.height_cm / 2.54
            feet = int(total_inches // 12)
            inches = int(total_inches % 12)
            form.height_ft.data = str(feet) if 4 <= feet <= 7 else ''
            form.height_in.data = str(inches) if 0 <= inches <= 11 else ''
        
        form.has_children.data = profile.has_children
        form.wants_children.data = profile.wants_children
        form.smoking.data = profile.smoking
        form.drinking.data = profile.drinking
        
        # Traditional/Conservative values
        form.conservatism_level.data = profile.conservatism_level
        form.head_covering.data = profile.head_covering
        form.fasting_practice.data = profile.fasting_practice
        form.prayer_frequency.data = profile.prayer_frequency
        form.bible_reading.data = profile.bible_reading
        form.dietary_restrictions.data = profile.dietary_restrictions
        form.family_role_view.data = profile.family_role_view
        form.wants_spouse_same_denomination.data = profile.wants_spouse_same_denomination
        form.willing_to_relocate.data = profile.willing_to_relocate
        form.wants_church_wedding.data = profile.wants_church_wedding
        form.smoking.data = profile.smoking
        form.drinking.data = profile.drinking
        
        form.looking_for_gender.data = profile.looking_for_gender
        form.looking_for_age_min.data = profile.looking_for_age_min
        form.looking_for_age_max.data = profile.looking_for_age_max
        form.relationship_goal.data = profile.relationship_goal
    
    return render_template('profile/edit.html', form=form)


@profile_bp.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    """Manage profile photos."""
    form = PhotoUploadForm()
    
    if form.validate_on_submit() and form.photo.data:
        file = form.photo.data
        
        if file and allowed_file(file.filename):
            # Check photo limit
            photo_count = Photo.query.filter_by(user_id=current_user.id).count()
            if photo_count >= current_app.config['MAX_PHOTOS_PER_USER']:
                flash(f'Maximum {current_app.config["MAX_PHOTOS_PER_USER"]} photos allowed.', 'error')
                return redirect(url_for('profile.photos'))
            
            # Validate image file
            is_valid, error_msg = validate_image_file(file)
            if not is_valid:
                flash(error_msg, 'error')
                return redirect(url_for('profile.photos'))
            
            # Generate unique filenames
            unique_filename = generate_unique_filename(file.filename)
            thumb_filename = generate_unique_filename(file.filename, prefix='thumb_')
            
            # Process image (get bytes, not file path)
            success, error_msg, image_data = process_uploaded_image(
                file, 
                output_path=None,  # Return bytes instead of saving to file
                create_thumbnail=True
            )
            
            if not success:
                flash(f'Error processing image: {error_msg}', 'error')
                return redirect(url_for('profile.photos'))
            
            img_bytes, thumb_bytes = image_data
            
            # Upload to Azure Blob Storage (or local fallback)
            photo_url, storage_type = upload_photo_to_storage(img_bytes, unique_filename)
            
            thumbnail_url = None
            if thumb_bytes:
                thumbnail_url, _ = upload_photo_to_storage(thumb_bytes, thumb_filename)
            
            # Create photo record
            is_primary = photo_count == 0  # First photo is primary
            
            photo = Photo(
                user_id=current_user.id,
                filename=unique_filename,
                url=photo_url,
                thumbnail_url=thumbnail_url,
                is_primary=is_primary,
                display_order=photo_count
            )
            db.session.add(photo)
            db.session.commit()
            
            storage_msg = "Azure Blob" if storage_type == 'azure' else "local"
            current_app.logger.info(f"Photo uploaded to {storage_msg}: {unique_filename}")
            
            flash('Photo uploaded and optimized!', 'success')
            return redirect(url_for('profile.photos'))
        else:
            flash('Invalid file type. Please upload an image.', 'error')
    
    user_photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.display_order).all()
    return render_template('profile/photos.html', form=form, photos=user_photos)


@profile_bp.route('/photos/<int:photo_id>/delete', methods=['POST'])
@login_required
def delete_photo(photo_id):
    """Delete a photo."""
    photo = Photo.query.filter_by(id=photo_id, user_id=current_user.id).first_or_404()
    
    # Delete file from storage (Azure Blob or local)
    try:
        delete_photo_from_storage(photo.url)
        if photo.thumbnail_url:
            delete_photo_from_storage(photo.thumbnail_url)
    except Exception as e:
        current_app.logger.warning(f"Failed to delete photo file: {e}")
    
    was_primary = photo.is_primary
    db.session.delete(photo)
    db.session.commit()
    
    # If deleted photo was primary, make another one primary
    if was_primary:
        next_photo = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.display_order).first()
        if next_photo:
            next_photo.is_primary = True
            db.session.commit()
    
    flash('Photo deleted.', 'success')
    return redirect(url_for('profile.photos'))


@profile_bp.route('/photos/<int:photo_id>/primary', methods=['POST'])
@login_required
def set_primary_photo(photo_id):
    """Set a photo as primary."""
    Photo.set_primary(current_user.id, photo_id)
    flash('Primary photo updated.', 'success')
    return redirect(url_for('profile.photos'))


@profile_bp.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    """View another user's profile."""
    if user_id == current_user.id:
        return redirect(url_for('profile.view'))

    user = User.query.get_or_404(user_id)

    # Check if user is approved and active
    if not user.is_active or not user.is_approved:
        flash('This profile is not available.', 'error')
        return redirect(url_for('discover.browse'))

    # Check if blocked
    if current_user.has_blocked(user) or current_user.is_blocked_by(user):
        flash('This profile is not available.', 'error')
        return redirect(url_for('discover.browse'))

    # Check if matched
    is_matched = current_user.is_matched_with(user)
    has_liked = current_user.has_liked(user)

    # Privacy settings - only show what user allows
    privacy_context = {
        'can_see_online_status': user.show_online,
        'can_see_distance': user.show_distance,
    }

    return render_template('profile/view.html',
                          user=user,
                          is_own_profile=False,
                          is_matched=is_matched,
                          has_liked=has_liked,
                          privacy=privacy_context)

