"""Photo model for user profile photos."""
from datetime import datetime
from app.extensions import db


class Photo(db.Model):
    """User profile photos."""
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Storage
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    
    # Metadata
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    
    # Moderation - photos require approval before being shown
    is_approved = db.Column(db.Boolean, default=False)
    moderation_status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    moderation_notes = db.Column(db.Text)  # Admin notes for rejection reason
    moderated_at = db.Column(db.DateTime)
    moderated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def set_primary(user_id, photo_id):
        """Set a photo as primary, unsetting others."""
        # Unset all other primary photos for this user
        Photo.query.filter_by(user_id=user_id, is_primary=True).update({'is_primary': False})
        
        # Set the new primary
        photo = Photo.query.filter_by(id=photo_id, user_id=user_id).first()
        if photo:
            photo.is_primary = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def reorder_photos(user_id, photo_order):
        """Reorder photos for a user. photo_order is a list of photo IDs in desired order."""
        for order, photo_id in enumerate(photo_order):
            Photo.query.filter_by(id=photo_id, user_id=user_id).update({'display_order': order})
        db.session.commit()

    def approve(self, admin_id=None):
        """Approve this photo for display."""
        self.is_approved = True
        self.moderation_status = 'approved'
        self.moderated_at = datetime.utcnow()
        self.moderated_by_id = admin_id
        db.session.commit()

    def reject(self, admin_id=None, notes=None):
        """Reject this photo."""
        self.is_approved = False
        self.moderation_status = 'rejected'
        self.moderation_notes = notes
        self.moderated_at = datetime.utcnow()
        self.moderated_by_id = admin_id
        db.session.commit()

    @staticmethod
    def get_pending_photos():
        """Get all photos pending moderation."""
        return Photo.query.filter_by(moderation_status='pending').order_by(Photo.created_at.asc()).all()

    @staticmethod
    def get_pending_count():
        """Get count of photos pending moderation."""
        return Photo.query.filter_by(moderation_status='pending').count()

    def __repr__(self):
        return f'<Photo {self.id} (User {self.user_id})>'

