"""Block and Report models for safety features."""
from datetime import datetime
from app.extensions import db


class Block(db.Model):
    """Record of one user blocking another."""
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),
    )
    
    @staticmethod
    def block_user(blocker_id, blocked_id):
        """Block a user. Also removes any existing match."""
        # Check if already blocked
        existing = Block.query.filter_by(blocker_id=blocker_id, blocked_id=blocked_id).first()
        if existing:
            return existing
        
        block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
        db.session.add(block)
        
        # Deactivate any existing match
        from app.models.match import Match
        match = Match.get_match(blocker_id, blocked_id)
        if match:
            match.unmatch(blocker_id)
        
        db.session.commit()
        return block
    
    @staticmethod
    def unblock_user(blocker_id, blocked_id):
        """Remove a block."""
        block = Block.query.filter_by(blocker_id=blocker_id, blocked_id=blocked_id).first()
        if block:
            db.session.delete(block)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_blocked_ids(user_id):
        """Get list of user IDs blocked by this user."""
        blocks = Block.query.filter_by(blocker_id=user_id).all()
        return [b.blocked_id for b in blocks]
    
    @staticmethod
    def get_blocker_ids(user_id):
        """Get list of user IDs who have blocked this user."""
        blocks = Block.query.filter_by(blocked_id=user_id).all()
        return [b.blocker_id for b in blocks]
    
    def __repr__(self):
        return f'<Block {self.blocker_id} blocked {self.blocked_id}>'


class Report(db.Model):
    """Reports submitted by users about other users."""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # NULL = auto-moderation
    reported_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    reason = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)  # Detailed description from reporter
    
    # Admin handling
    status = db.Column(db.String(20), default='pending')  # 'pending', 'resolved', 'dismissed'
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported = db.relationship('User', foreign_keys=[reported_id])
    resolver = db.relationship('User', foreign_keys=[resolved_by_id])
    
    REASON_CHOICES = [
        ('fake_profile', 'Fake Profile'),
        ('inappropriate_photos', 'Inappropriate Photos'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('underage', 'Appears Underage'),
        ('scam', 'Scam/Fraud'),
        ('other', 'Other'),
    ]
    
    @staticmethod
    def create_report(reporter_id, reported_id, reason, description=None):
        """Create a new report."""
        report = Report(
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            description=description
        )
        db.session.add(report)
        db.session.commit()
        return report
    
    def resolve(self, admin_id, status, notes=None):
        """Mark report as resolved by admin."""
        self.resolved_by_id = admin_id
        self.resolved_at = datetime.utcnow()
        self.status = status
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    @property
    def is_auto_generated(self):
        """Check if this is a system/auto-moderation report."""
        return self.reporter_id is None

    @property
    def reporter_display(self):
        """Get reporter display name or 'System' for auto-moderation."""
        if self.reporter_id is None:
            return "System (Auto-Moderation)"
        return self.reporter.display_name if self.reporter else "Unknown"

    def get_reason_display(self):
        """Get human-readable reason."""
        if self.reason == 'auto_moderation':
            return 'Auto-Moderation Flag'
        for code, display in self.REASON_CHOICES:
            if code == self.reason:
                return display
        return self.reason
    
    def __repr__(self):
        return f'<Report {self.id}: {self.reporter_id} reported {self.reported_id}>'

