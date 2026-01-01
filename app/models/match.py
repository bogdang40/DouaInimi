"""Like, Match, and Pass models for the matching system."""
from datetime import datetime
from app.extensions import db


class Pass(db.Model):
    """Record of one user passing (swiping left) on another."""
    __tablename__ = 'passes'

    id = db.Column(db.Integer, primary_key=True)
    passer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    passed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('passer_id', 'passed_id', name='unique_pass'),
    )
    
    @staticmethod
    def create_pass(passer_id, passed_id):
        """Create a pass record."""
        existing = Pass.query.filter_by(passer_id=passer_id, passed_id=passed_id).first()
        if existing:
            return existing
        
        pass_record = Pass(passer_id=passer_id, passed_id=passed_id)
        db.session.add(pass_record)
        db.session.commit()
        return pass_record
    
    @staticmethod
    def get_passed_ids(user_id):
        """Get list of user IDs this user has passed on."""
        passes = Pass.query.filter_by(passer_id=user_id).all()
        return [p.passed_id for p in passes]
    
    def __repr__(self):
        return f'<Pass {self.passer_id} passed on {self.passed_id}>'


class Like(db.Model):
    """Record of one user liking another."""
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    liker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    liked_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    is_super_like = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint('liker_id', 'liked_id', name='unique_like'),
        # For super like count queries: WHERE liker_id=X AND is_super_like=true AND created_at>=Y
        db.Index('ix_likes_super', 'liker_id', 'is_super_like', 'created_at'),
        # For checking mutual likes: WHERE liked_id=X (find people who liked me)
        db.Index('ix_likes_received', 'liked_id', 'created_at'),
    )
    
    # Super like limits
    SUPER_LIKES_PER_DAY = 3  # Free users get 3 super likes per day
    PREMIUM_SUPER_LIKES_PER_DAY = 10  # Premium users get more
    
    @staticmethod
    def get_super_likes_today(user_id):
        """Get count of super likes used today by a user."""
        from datetime import date
        today_start = datetime.combine(date.today(), datetime.min.time())
        return Like.query.filter(
            Like.liker_id == user_id,
            Like.is_super_like == True,
            Like.created_at >= today_start
        ).count()
    
    @staticmethod
    def can_super_like(user_id, is_premium=False):
        """Check if user can send another super like today."""
        used_today = Like.get_super_likes_today(user_id)
        limit = Like.PREMIUM_SUPER_LIKES_PER_DAY if is_premium else Like.SUPER_LIKES_PER_DAY
        return used_today < limit
    
    @staticmethod
    def super_likes_remaining(user_id, is_premium=False):
        """Get number of super likes remaining today."""
        used_today = Like.get_super_likes_today(user_id)
        limit = Like.PREMIUM_SUPER_LIKES_PER_DAY if is_premium else Like.SUPER_LIKES_PER_DAY
        return max(0, limit - used_today)
    
    @staticmethod
    def create_like(liker_id, liked_id, is_super=False):
        """Create a like and check for mutual match."""
        # Check if like already exists
        existing = Like.query.filter_by(liker_id=liker_id, liked_id=liked_id).first()
        if existing:
            return existing, False  # Like exists, no new match
        
        # Create the like
        like = Like(liker_id=liker_id, liked_id=liked_id, is_super_like=is_super)
        db.session.add(like)
        
        # Check if the other person has already liked us (mutual match!)
        mutual_like = Like.query.filter_by(liker_id=liked_id, liked_id=liker_id).first()
        
        is_match = False
        if mutual_like:
            # It's a match! Create a Match record
            match = Match.create_match(liker_id, liked_id)
            if match:
                is_match = True
        
        db.session.commit()
        return like, is_match
    
    def __repr__(self):
        return f'<Like {self.liker_id} -> {self.liked_id}>'


class Match(db.Model):
    """Record of a mutual match between two users."""
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    matched_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Status
    is_active = db.Column(db.Boolean, default=True, index=True)
    unmatched_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    unmatched_at = db.Column(db.DateTime)

    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    messages = db.relationship('Message', backref='match', cascade='all, delete-orphan',
                               order_by='Message.created_at')

    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_match'),
        db.CheckConstraint('user1_id < user2_id', name='ordered_user_ids'),
        # Composite index for finding user's active matches
        db.Index('ix_matches_user1_active', 'user1_id', 'is_active'),
        db.Index('ix_matches_user2_active', 'user2_id', 'is_active'),
    )
    
    @staticmethod
    def create_match(user_a_id, user_b_id):
        """Create a match between two users. Always stores lower ID as user1_id."""
        user1_id = min(user_a_id, user_b_id)
        user2_id = max(user_a_id, user_b_id)

        # Check if match already exists
        existing = Match.query.filter_by(user1_id=user1_id, user2_id=user2_id).first()
        if existing:
            return existing

        match = Match(user1_id=user1_id, user2_id=user2_id)
        db.session.add(match)

        # Send email notifications to both users (if they have notifications enabled)
        try:
            Match._send_match_notifications(user1_id, user2_id)
        except Exception:
            pass  # Don't fail match creation if email fails

        return match

    @staticmethod
    def _send_match_notifications(user1_id, user2_id):
        """Send email notifications to both users about the new match."""
        from flask import current_app
        from app.models.user import User

        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)

        if not user1 or not user2:
            return

        try:
            from app.services.email import send_new_match_email

            # Notify user1 if they have notifications enabled
            if user1.notify_matches:
                send_new_match_email(user1, user2)

            # Notify user2 if they have notifications enabled
            if user2.notify_matches:
                send_new_match_email(user2, user1)
        except Exception as e:
            current_app.logger.error(f"Failed to send match notification: {e}")
    
    @staticmethod
    def get_match(user_a_id, user_b_id):
        """Get match between two users if it exists."""
        user1_id = min(user_a_id, user_b_id)
        user2_id = max(user_a_id, user_b_id)
        return Match.query.filter_by(user1_id=user1_id, user2_id=user2_id, is_active=True).first()
    
    @staticmethod
    def get_user_matches(user_id):
        """Get all active matches for a user."""
        return Match.query.filter(
            db.or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        ).order_by(Match.matched_at.desc()).all()

    @staticmethod
    def get_user_matches_with_details(user_id):
        """Get all active matches with last message and unread count in a single query.

        OPTIMIZED: Returns matches with precomputed last_message_id, last_message_time,
        and unread_count to avoid N+1 queries.
        """
        from app.models.message import Message
        from sqlalchemy import func, case, and_, desc
        from sqlalchemy.orm import aliased

        # Subquery for last message per match
        last_msg_subq = db.session.query(
            Message.match_id,
            func.max(Message.id).label('last_message_id'),
            func.max(Message.created_at).label('last_message_time')
        ).group_by(Message.match_id).subquery()

        # Subquery for unread count per match
        unread_subq = db.session.query(
            Message.match_id,
            func.count(Message.id).label('unread_count')
        ).filter(
            Message.sender_id != user_id,
            Message.is_read == False
        ).group_by(Message.match_id).subquery()

        # Main query with joins
        results = db.session.query(
            Match,
            last_msg_subq.c.last_message_id,
            last_msg_subq.c.last_message_time,
            func.coalesce(unread_subq.c.unread_count, 0).label('unread_count')
        ).outerjoin(
            last_msg_subq, Match.id == last_msg_subq.c.match_id
        ).outerjoin(
            unread_subq, Match.id == unread_subq.c.match_id
        ).filter(
            db.or_(Match.user1_id == user_id, Match.user2_id == user_id),
            Match.is_active == True
        ).order_by(Match.matched_at.desc()).all()

        # Fetch all last messages in a single query
        last_message_ids = [r.last_message_id for r in results if r.last_message_id]
        last_messages = {}
        if last_message_ids:
            messages = Message.query.filter(Message.id.in_(last_message_ids)).all()
            last_messages = {m.id: m for m in messages}

        # Build result list with all data attached
        match_data = []
        for result in results:
            match = result[0]
            match._cached_last_message = last_messages.get(result.last_message_id)
            match._cached_last_message_time = result.last_message_time
            match._cached_unread_count = result.unread_count
            match_data.append(match)

        return match_data

    def get_cached_last_message(self):
        """Get cached last message (use after get_user_matches_with_details)."""
        return getattr(self, '_cached_last_message', None)

    def get_cached_unread_count(self, user_id=None):
        """Get cached unread count (use after get_user_matches_with_details)."""
        return getattr(self, '_cached_unread_count', 0)
    
    def get_other_user(self, user_id):
        """Get the other user in the match."""
        if self.user1_id == user_id:
            return self.user2
        return self.user1
    
    def get_other_user_id(self, user_id):
        """Get the other user's ID in the match."""
        if self.user1_id == user_id:
            return self.user2_id
        return self.user1_id
    
    def unmatch(self, user_id):
        """Unmatch (deactivate) the match."""
        self.is_active = False
        self.unmatched_by = user_id
        self.unmatched_at = datetime.utcnow()
        db.session.commit()
    
    @property
    def last_message(self):
        """Get the most recent message in this match."""
        from app.models.message import Message
        return Message.query.filter_by(match_id=self.id).order_by(Message.created_at.desc()).first()
    
    def unread_count(self, user_id):
        """Get count of unread messages for a user."""
        from app.models.message import Message
        return Message.query.filter(
            Message.match_id == self.id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).count()
    
    def __repr__(self):
        return f'<Match {self.user1_id} <-> {self.user2_id}>'

