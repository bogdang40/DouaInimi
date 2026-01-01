"""Message model for chat functionality."""
from datetime import datetime
from app.extensions import db


class Message(db.Model):
    """Chat messages between matched users."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    content = db.Column(db.Text, nullable=False)

    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    # Soft delete per user
    deleted_by_sender = db.Column(db.Boolean, default=False)
    deleted_by_receiver = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite indices for common query patterns
    __table_args__ = (
        # For unread message count queries: WHERE match_id=X AND sender_id!=Y AND is_read=false
        db.Index('ix_messages_unread', 'match_id', 'sender_id', 'is_read'),
        # For message ordering within a conversation
        db.Index('ix_messages_match_created', 'match_id', 'created_at'),
    )
    
    @staticmethod
    def send_message(match_id, sender_id, content):
        """Send a new message."""
        message = Message(
            match_id=match_id,
            sender_id=sender_id,
            content=content.strip()
        )
        db.session.add(message)
        db.session.commit()

        # Send email notification to recipient (async, non-blocking)
        try:
            Message._send_message_notification(match_id, sender_id, content.strip())
        except Exception:
            pass  # Don't fail message send if notification fails

        return message

    @staticmethod
    def _send_message_notification(match_id, sender_id, content):
        """Send email notification to the message recipient."""
        from flask import current_app
        from app.models.match import Match
        from app.models.user import User

        try:
            match = Match.query.get(match_id)
            if not match:
                return

            sender = User.query.get(sender_id)
            if not sender:
                return

            # Get recipient
            recipient_id = match.get_other_user_id(sender_id)
            recipient = User.query.get(recipient_id)
            if not recipient:
                return

            # Check if recipient has message notifications enabled
            if not recipient.notify_messages:
                return

            # Only notify if recipient is not currently active (online)
            # to avoid spamming them while they're chatting
            if recipient.is_online:
                return

            from app.services.email import send_new_message_email

            # Create a preview (first 100 chars)
            preview = content[:100] + ('...' if len(content) > 100 else '')
            send_new_message_email(recipient, sender, preview)
        except Exception as e:
            current_app.logger.error(f"Failed to send message notification: {e}")
    
    @staticmethod
    def get_conversation(match_id, user_id, limit=50, before_id=None):
        """Get messages for a conversation, excluding deleted ones for this user."""
        query = Message.query.filter_by(match_id=match_id)
        
        # Exclude messages deleted by this user
        query = query.filter(
            db.or_(
                db.and_(Message.sender_id == user_id, Message.deleted_by_sender == False),
                db.and_(Message.sender_id != user_id, Message.deleted_by_receiver == False)
            )
        )
        
        if before_id:
            query = query.filter(Message.id < before_id)
        
        return query.order_by(Message.created_at.desc()).limit(limit).all()[::-1]
    
    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    def mark_conversation_read(match_id, user_id):
        """Mark all messages in a conversation as read for a user."""
        Message.query.filter(
            Message.match_id == match_id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        db.session.commit()
    
    def delete_for_user(self, user_id):
        """Soft delete message for a specific user."""
        if self.sender_id == user_id:
            self.deleted_by_sender = True
        else:
            self.deleted_by_receiver = True
        db.session.commit()
    
    @property
    def time_ago(self):
        """Get human-readable time ago string."""
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years}y ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"
    
    def __repr__(self):
        return f'<Message {self.id} in Match {self.match_id}>'

