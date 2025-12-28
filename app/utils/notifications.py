"""Push notification utilities for browser notifications."""
from datetime import datetime


def get_notification_payload(notification_type, data):
    """
    Generate notification payload for different event types.
    
    Args:
        notification_type: Type of notification ('new_match', 'new_message', 'super_like', etc.)
        data: Dict containing notification-specific data
    
    Returns:
        Dict with title, body, icon, url, and other notification options
    """
    base_icon = '/static/images/logo.png'
    badge_icon = '/static/icons/icon-72x72.png'
    
    notifications = {
        'new_match': {
            'title': "💕 It's a Match!",
            'body': f"You and {data.get('user_name', 'Someone')} have liked each other!",
            'icon': data.get('user_photo', base_icon),
            'badge': badge_icon,
            'tag': f"match-{data.get('match_id', '')}",
            'url': f"/messages/{data.get('match_id', '')}",
            'vibrate': [200, 100, 200, 100, 200],
            'requireInteraction': True,
        },
        'new_message': {
            'title': f"💬 {data.get('sender_name', 'Someone')}",
            'body': data.get('message_preview', 'Sent you a message'),
            'icon': data.get('sender_photo', base_icon),
            'badge': badge_icon,
            'tag': f"message-{data.get('match_id', '')}",
            'url': f"/messages/{data.get('match_id', '')}",
            'vibrate': [100, 50, 100],
            'renotify': True,  # Alert again for same conversation
        },
        'super_like': {
            'title': "⭐ Super Liked!",
            'body': f"{data.get('user_name', 'Someone')} super liked you!",
            'icon': data.get('user_photo', base_icon),
            'badge': badge_icon,
            'tag': f"superlike-{data.get('user_id', '')}",
            'url': '/discover',
            'vibrate': [100, 100, 100, 100, 200],
            'requireInteraction': True,
        },
        'profile_view': {
            'title': "👀 Profile Viewed",
            'body': f"{data.get('user_name', 'Someone')} viewed your profile",
            'icon': data.get('user_photo', base_icon),
            'badge': badge_icon,
            'tag': 'profile-view',
            'url': '/discover',
            'silent': True,  # Don't make sound
        },
    }
    
    return notifications.get(notification_type, {
        'title': 'Două Inimi',
        'body': 'You have a new notification',
        'icon': base_icon,
        'url': '/',
    })


class NotificationService:
    """Service for managing push notifications."""
    
    @staticmethod
    def notify_new_match(match):
        """
        Send notification for a new match.
        Called when a mutual like creates a match.
        """
        # Get both users
        user1 = match.user1
        user2 = match.user2
        
        # Notify user1 about user2
        payload1 = get_notification_payload('new_match', {
            'user_name': user2.display_name,
            'user_photo': user2.primary_photo_url,
            'match_id': match.id,
        })
        
        # Notify user2 about user1
        payload2 = get_notification_payload('new_match', {
            'user_name': user1.display_name,
            'user_photo': user1.primary_photo_url,
            'match_id': match.id,
        })
        
        # In production, these would be sent via Web Push API
        # For now, we'll emit via Socket.IO if available
        return payload1, payload2
    
    @staticmethod
    def notify_new_message(message, sender, recipient):
        """
        Send notification for a new message.
        """
        preview = message.content[:50] + '...' if len(message.content) > 50 else message.content
        
        payload = get_notification_payload('new_message', {
            'sender_name': sender.display_name,
            'sender_photo': sender.primary_photo_url,
            'message_preview': preview,
            'match_id': message.match_id,
        })
        
        return payload
    
    @staticmethod
    def notify_super_like(liker, liked_user):
        """
        Send notification when someone super likes.
        """
        payload = get_notification_payload('super_like', {
            'user_name': liker.display_name,
            'user_photo': liker.primary_photo_url,
            'user_id': liker.id,
        })
        
        return payload

