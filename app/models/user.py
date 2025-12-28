"""User model for authentication."""
from datetime import datetime
import secrets
from flask_login import UserMixin
from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    """User model for authentication and account management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Status flags
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Admin must approve new users
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_paused = db.Column(db.Boolean, default=False)  # Hide from search
    
    # Privacy settings
    show_online = db.Column(db.Boolean, default=True)
    show_distance = db.Column(db.Boolean, default=True)
    
    # Notification settings
    notify_matches = db.Column(db.Boolean, default=True)
    notify_messages = db.Column(db.Boolean, default=True)
    
    # Verification tokens
    verification_token = db.Column(db.String(100))
    verification_token_expires = db.Column(db.DateTime)
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    
    # Activity tracking
    email_verified_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Online status (considered online if active within last 5 minutes)
    ONLINE_THRESHOLD_MINUTES = 5
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, 
                              cascade='all, delete-orphan', lazy='joined')
    photos = db.relationship('Photo', backref='user', cascade='all, delete-orphan',
                             order_by='Photo.display_order')
    
    # Likes sent and received
    likes_sent = db.relationship('Like', foreign_keys='Like.liker_id',
                                  backref='liker', cascade='all, delete-orphan')
    likes_received = db.relationship('Like', foreign_keys='Like.liked_id',
                                      backref='liked', cascade='all, delete-orphan')
    
    # Messages
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id',
                                     backref='sender', cascade='all, delete-orphan')
    
    # Blocks and reports
    blocks_made = db.relationship('Block', foreign_keys='Block.blocker_id',
                                   backref='blocker', cascade='all, delete-orphan')
    blocks_received = db.relationship('Block', foreign_keys='Block.blocked_id',
                                       backref='blocked', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """Generate email verification token."""
        from datetime import timedelta
        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token
    
    def generate_reset_token(self):
        """Generate password reset token."""
        from datetime import timedelta
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_email(self):
        """Mark email as verified."""
        self.is_verified = True
        self.email_verified_at = datetime.utcnow()
        self.verification_token = None
        self.verification_token_expires = None
    
    def update_last_active(self):
        """Update last active timestamp."""
        self.last_active = datetime.utcnow()
    
    @property
    def is_online(self):
        """Check if user is currently online (active within threshold)."""
        if not self.last_active:
            return False
        from datetime import timedelta
        threshold = datetime.utcnow() - timedelta(minutes=self.ONLINE_THRESHOLD_MINUTES)
        return self.last_active > threshold
    
    @property
    def online_status_text(self):
        """Get human-readable online status."""
        if self.is_online:
            return "Online now"
        if not self.last_active:
            return "Offline"
        
        from datetime import timedelta
        now = datetime.utcnow()
        diff = now - self.last_active
        
        if diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"Active {minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"Active {hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"Active {days}d ago"
        else:
            return "Active recently"
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        self.last_active = datetime.utcnow()
    
    @property
    def age(self):
        """Calculate age from profile date of birth."""
        if self.profile and self.profile.date_of_birth:
            today = datetime.today()
            born = self.profile.date_of_birth
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None
    
    @property
    def display_name(self):
        """Get display name from profile or email."""
        if self.profile and self.profile.first_name:
            return self.profile.first_name
        return self.email.split('@')[0]
    
    @property
    def primary_photo(self):
        """Get primary photo or first photo."""
        primary = Photo.query.filter_by(user_id=self.id, is_primary=True).first()
        if primary:
            return primary
        return Photo.query.filter_by(user_id=self.id).order_by(Photo.display_order).first()
    
    @property
    def primary_photo_url(self):
        """Get primary photo URL or default avatar."""
        photo = self.primary_photo
        if photo:
            return photo.url
        return '/static/images/default-avatar.svg'
    
    @property
    def profile_complete(self):
        """Check if profile is complete."""
        if not self.profile:
            return False
        return self.profile.is_complete
    
    def has_liked(self, user):
        """Check if this user has liked another user."""
        from app.models.match import Like
        return Like.query.filter_by(liker_id=self.id, liked_id=user.id).first() is not None
    
    def is_matched_with(self, user):
        """Check if matched with another user."""
        from app.models.match import Match
        return Match.get_match(self.id, user.id) is not None
    
    def has_blocked(self, user):
        """Check if this user has blocked another user."""
        from app.models.report import Block
        return Block.query.filter_by(blocker_id=self.id, blocked_id=user.id).first() is not None
    
    def is_blocked_by(self, user):
        """Check if this user is blocked by another user."""
        from app.models.report import Block
        return Block.query.filter_by(blocker_id=user.id, blocked_id=self.id).first() is not None
    
    def __repr__(self):
        return f'<User {self.email}>'


# Import Photo here to avoid circular imports
from app.models.photo import Photo

