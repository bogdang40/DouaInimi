"""Email notification service for matches, messages, etc."""
from flask import current_app, render_template_string
from app.services.email import send_email_direct


# Email templates as strings (could also use files)
NEW_MATCH_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Georgia, serif; background: #f8f8f8; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #f59e0b, #f97316); padding: 30px; text-align: center; color: white; }
        .header h1 { margin: 0; font-size: 28px; }
        .content { padding: 30px; text-align: center; }
        .photo { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid #f59e0b; margin: 0 auto 20px; }
        .name { font-size: 24px; color: #333; margin-bottom: 10px; }
        .message { color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }
        .btn { display: inline-block; background: linear-gradient(135deg, #f59e0b, #f97316); color: white; text-decoration: none; padding: 14px 30px; border-radius: 30px; font-weight: bold; font-size: 16px; }
        .footer { padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💕 It's a Match!</h1>
        </div>
        <div class="content">
            <img src="{{ match_photo }}" alt="{{ match_name }}" class="photo" onerror="this.style.display='none'">
            <div class="name">{{ match_name }}</div>
            <p class="message">
                You and {{ match_name }} have liked each other! 
                Start a conversation and see where it goes.
            </p>
            <a href="{{ app_url }}/messages/{{ match_id }}" class="btn">Say Hello 👋</a>
        </div>
        <div class="footer">
            <p>Două Inimi - Connecting Romanian Christians</p>
            <p><a href="{{ app_url }}/settings" style="color: #999;">Manage email preferences</a></p>
        </div>
    </div>
</body>
</html>
"""

NEW_MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Georgia, serif; background: #f8f8f8; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { background: #1e1e2e; padding: 20px; }
        .header-content { display: flex; align-items: center; }
        .photo { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px; }
        .sender-info { color: white; }
        .sender-name { font-size: 18px; font-weight: bold; margin: 0; }
        .sender-action { font-size: 14px; opacity: 0.8; margin: 0; }
        .content { padding: 30px; }
        .message-bubble { background: #f3f4f6; border-radius: 20px; padding: 20px; margin-bottom: 30px; }
        .message-text { color: #333; font-size: 16px; line-height: 1.6; margin: 0; }
        .btn { display: inline-block; background: linear-gradient(135deg, #f59e0b, #f97316); color: white; text-decoration: none; padding: 14px 30px; border-radius: 30px; font-weight: bold; font-size: 16px; }
        .footer { padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <img src="{{ sender_photo }}" alt="{{ sender_name }}" class="photo" onerror="this.style.display='none'">
                <div class="sender-info">
                    <p class="sender-name">{{ sender_name }}</p>
                    <p class="sender-action">sent you a message</p>
                </div>
            </div>
        </div>
        <div class="content">
            <div class="message-bubble">
                <p class="message-text">"{{ message_preview }}"</p>
            </div>
            <a href="{{ app_url }}/messages/{{ match_id }}" class="btn">Reply Now 💬</a>
        </div>
        <div class="footer">
            <p>Două Inimi - Connecting Romanian Christians</p>
            <p><a href="{{ app_url }}/settings" style="color: #999;">Manage email preferences</a></p>
        </div>
    </div>
</body>
</html>
"""

SUPER_LIKE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Georgia, serif; background: #f8f8f8; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 30px; text-align: center; color: white; }
        .header h1 { margin: 0; font-size: 28px; }
        .content { padding: 30px; text-align: center; }
        .photo { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 4px solid #3b82f6; margin: 0 auto 20px; }
        .name { font-size: 24px; color: #333; margin-bottom: 10px; }
        .message { color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }
        .btn { display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; text-decoration: none; padding: 14px 30px; border-radius: 30px; font-weight: bold; font-size: 16px; }
        .footer { padding: 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⭐ Super Liked!</h1>
        </div>
        <div class="content">
            <img src="{{ liker_photo }}" alt="{{ liker_name }}" class="photo" onerror="this.style.display='none'">
            <div class="name">{{ liker_name }}</div>
            <p class="message">
                {{ liker_name }} thinks you're special and sent you a Super Like!
                Check out their profile and see if you feel the same.
            </p>
            <a href="{{ app_url }}/discover" class="btn">See Who ⭐</a>
        </div>
        <div class="footer">
            <p>Două Inimi - Connecting Romanian Christians</p>
            <p><a href="{{ app_url }}/settings" style="color: #999;">Manage email preferences</a></p>
        </div>
    </div>
</body>
</html>
"""


class EmailNotificationService:
    """Service for sending email notifications."""
    
    @staticmethod
    def get_app_url():
        """Get the base application URL."""
        return current_app.config.get('APP_URL', 'http://localhost:5001')
    
    @staticmethod
    def send_new_match_email(recipient, match_user, match):
        """Send email notification for a new match."""
        try:
            html = render_template_string(
                NEW_MATCH_TEMPLATE,
                match_name=match_user.display_name,
                match_photo=match_user.primary_photo_url,
                match_id=match.id,
                app_url=EmailNotificationService.get_app_url()
            )
            
            send_email_direct(
                subject=f"💕 It's a Match! You matched with {match_user.display_name}",
                recipients=[recipient.email],
                html_body=html,
                text_body=f"You matched with {match_user.display_name}! Start chatting now."
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send match email: {e}")
            return False
    
    @staticmethod
    def send_new_message_email(recipient, sender, message, match):
        """Send email notification for a new message."""
        try:
            preview = message.content[:100] + '...' if len(message.content) > 100 else message.content
            
            html = render_template_string(
                NEW_MESSAGE_TEMPLATE,
                sender_name=sender.display_name,
                sender_photo=sender.primary_photo_url,
                message_preview=preview,
                match_id=match.id,
                app_url=EmailNotificationService.get_app_url()
            )
            
            send_email_direct(
                subject=f"💬 New message from {sender.display_name}",
                recipients=[recipient.email],
                html_body=html,
                text_body=f"{sender.display_name}: {preview}"
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send message email: {e}")
            return False
    
    @staticmethod
    def send_super_like_email(recipient, liker):
        """Send email notification for a super like."""
        try:
            html = render_template_string(
                SUPER_LIKE_TEMPLATE,
                liker_name=liker.display_name,
                liker_photo=liker.primary_photo_url,
                app_url=EmailNotificationService.get_app_url()
            )
            
            send_email_direct(
                subject=f"⭐ {liker.display_name} Super Liked you!",
                recipients=[recipient.email],
                html_body=html,
                text_body=f"{liker.display_name} super liked you! Check them out on Două Inimi."
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send super like email: {e}")
            return False

