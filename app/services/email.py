"""Email service for sending transactional emails."""
from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {e}")


def send_email(subject, recipient, template, **kwargs):
    """
    Send an email using a template.
    
    Args:
        subject: Email subject
        recipient: Recipient email address
        template: Template name without extension (e.g., 'auth/verify_email')
        **kwargs: Variables to pass to the template
    """
    app = current_app._get_current_object()
    
    msg = Message(
        subject=f"{current_app.config.get('APP_NAME', 'Două Inimi')} - {subject}",
        recipients=[recipient],
        sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@douainimi.com')
    )
    
    # Render HTML and plain text versions
    try:
        msg.html = render_template(f'emails/{template}.html', **kwargs)
    except Exception:
        msg.html = None
    
    try:
        msg.body = render_template(f'emails/{template}.txt', **kwargs)
    except Exception:
        # Fallback to a simple text version
        msg.body = f"Please visit the app to complete this action."
    
    # Send asynchronously in production, synchronously in development
    if current_app.config.get('MAIL_SUPPRESS_SEND', False):
        # Log email instead of sending in dev mode
        current_app.logger.info(f"[EMAIL] To: {recipient}, Subject: {subject}")
        return True
    
    try:
        thread = Thread(target=send_async_email, args=[app, msg])
        thread.start()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False


def send_verification_email(user):
    """Send email verification link to user."""
    verification_url = url_for('auth.verify_email', 
                               token=user.verification_token, 
                               _external=True)
    
    return send_email(
        subject="Verify Your Email",
        recipient=user.email,
        template="verify_email",
        user=user,
        verification_url=verification_url
    )


def send_password_reset_email(user):
    """Send password reset link to user."""
    reset_url = url_for('auth.reset_password', 
                        token=user.reset_token, 
                        _external=True)
    
    return send_email(
        subject="Reset Your Password",
        recipient=user.email,
        template="reset_password",
        user=user,
        reset_url=reset_url
    )


def send_new_match_email(user, matched_user):
    """Send notification about a new match."""
    match_url = url_for('matches.list', _external=True)
    
    return send_email(
        subject="You Have a New Match! 💕",
        recipient=user.email,
        template="new_match",
        user=user,
        matched_user=matched_user,
        match_url=match_url
    )


def send_new_message_email(user, sender, message_preview):
    """Send notification about a new message."""
    messages_url = url_for('messages.inbox', _external=True)

    return send_email(
        subject=f"New Message from {sender.display_name}",
        recipient=user.email,
        template="new_message",
        user=user,
        sender=sender,
        message_preview=message_preview,
        messages_url=messages_url
    )


def send_email_direct(subject, recipients, html_body, text_body=None):
    """
    Send an email with direct HTML/text content (no template).
    Used by EmailNotificationService for inline templates.

    Args:
        subject: Email subject
        recipients: List of recipient email addresses
        html_body: HTML content of the email
        text_body: Plain text content (optional fallback)
    """
    app = current_app._get_current_object()

    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@douainimi.com')
    )

    msg.html = html_body
    msg.body = text_body or "Please visit the app to view this notification."

    # Send asynchronously in production, log in development
    if current_app.config.get('MAIL_SUPPRESS_SEND', False):
        current_app.logger.info(f"[EMAIL] To: {recipients}, Subject: {subject}")
        return True

    try:
        thread = Thread(target=send_async_email, args=[app, msg])
        thread.start()
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {e}")
        return False

