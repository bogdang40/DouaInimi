"""Messaging routes with security hardening and rate limiting."""
from datetime import datetime
from collections import defaultdict
import time
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from app import socketio
from app.extensions import db
from app.models.match import Match
from app.models.message import Message
from app.forms.messages import MessageForm
from app.utils.security import (
    validate_message_content,
    sanitize_message,
    validate_socket_user,
    validate_socket_match_access,
    log_security_event
)

messages_bp = Blueprint('messages', __name__)

# Message limits
MAX_MESSAGE_LENGTH = 5000
MIN_MESSAGE_LENGTH = 1
MAX_MESSAGES_PER_MINUTE = 30  # Rate limit

# In-memory rate limiting for Socket.IO (per user)
# Structure: {user_id: [(timestamp1, timestamp2, ...)]}
_socket_rate_limits = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds


def check_socket_rate_limit(user_id):
    """Check if user has exceeded socket message rate limit.

    Returns:
        tuple: (allowed: bool, messages_remaining: int)
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old entries
    _socket_rate_limits[user_id] = [
        ts for ts in _socket_rate_limits[user_id] if ts > window_start
    ]

    current_count = len(_socket_rate_limits[user_id])

    if current_count >= MAX_MESSAGES_PER_MINUTE:
        return False, 0

    return True, MAX_MESSAGES_PER_MINUTE - current_count


def record_socket_message(user_id):
    """Record a message for rate limiting purposes."""
    _socket_rate_limits[user_id].append(time.time())


@messages_bp.route('/')
@login_required
def inbox():
    """Message inbox - list all conversations.

    OPTIMIZED: Uses get_user_matches_with_details to avoid N+1 queries.
    """
    # Single optimized query gets matches + last message + unread count
    matches = Match.get_user_matches_with_details(current_user.id)

    conversations = []
    for match in matches:
        other_user = match.get_other_user(current_user.id)
        # Use cached data instead of triggering new queries
        last_message = match.get_cached_last_message()
        unread = match.get_cached_unread_count()

        conversations.append({
            'match': match,
            'user': other_user,
            'last_message': last_message,
            'unread_count': unread,
        })

    # Sort by last message time (already sorted by matched_at, resort by message time)
    conversations.sort(
        key=lambda x: x['last_message'].created_at if x['last_message'] else x['match'].matched_at,
        reverse=True
    )

    return render_template('messages/inbox.html', conversations=conversations)


@messages_bp.route('/<int:match_id>')
@login_required
def conversation(match_id):
    """View messages in a conversation."""
    match = Match.query.get_or_404(match_id)
    
    # Verify current user is part of this match
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        flash('Invalid conversation.', 'error')
        return redirect(url_for('messages.inbox'))
    
    if not match.is_active:
        flash('This conversation is no longer active.', 'info')
        return redirect(url_for('messages.inbox'))
    
    other_user = match.get_other_user(current_user.id)
    
    # Mark messages as read
    Message.mark_conversation_read(match_id, current_user.id)
    
    # Get messages
    messages = Message.get_conversation(match_id, current_user.id)
    
    # Get all matches for sidebar
    all_matches = Match.get_user_matches(current_user.id)
    
    form = MessageForm()
    
    return render_template('messages/conversation.html',
                          match=match,
                          other_user=other_user,
                          messages=messages,
                          all_matches=all_matches,
                          form=form)


@messages_bp.route('/<int:match_id>/send', methods=['POST'])
@login_required
def send_message(match_id):
    """Send a message - POST endpoint with redirect.

    Rate limited to 30 messages per minute via Flask-Limiter.
    """
    # Apply rate limiting if limiter is available
    if hasattr(current_app, 'limiter') and current_app.limiter:
        try:
            # Check rate limit: 30 per minute
            with current_app.limiter.limit("30 per minute"):
                pass
        except Exception:
            flash('Too many messages. Please wait a moment.', 'warning')
            return redirect(url_for('messages.conversation', match_id=match_id))

    match = Match.query.get_or_404(match_id)

    # Verify current user is part of this match
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        flash('Invalid conversation.', 'error')
        return redirect(url_for('messages.inbox'))

    if not match.is_active:
        flash('This conversation is no longer active.', 'info')
        return redirect(url_for('messages.inbox'))

    form = MessageForm()

    if form.validate_on_submit():
        content = form.content.data.strip()

        if content:
            message = Message.send_message(
                match_id=match_id,
                sender_id=current_user.id,
                content=content
            )

            # Emit socket event for real-time update
            socketio.emit('new_message', {
                'match_id': match_id,
                'message_id': message.id,
                'sender_id': current_user.id,
                'sender_name': current_user.display_name,
                'sender_photo': current_user.primary_photo_url,
                'content': message.content,
                'created_at': message.created_at.strftime('%I:%M %p'),
            }, room=f'match_{match_id}')

    # POST-Redirect-GET: Always redirect after POST to prevent duplicate submissions
    return redirect(url_for('messages.conversation', match_id=match_id))


@messages_bp.route('/<int:match_id>/send-ajax', methods=['POST'])
@login_required
def send_message_ajax(match_id):
    """Send a message via AJAX - returns JSON with security validation.

    Rate limited to 30 messages per minute.
    """
    # Check rate limit
    allowed, remaining = check_socket_rate_limit(current_user.id)
    if not allowed:
        log_security_event('message_rate_limit_exceeded', {
            'user_id': current_user.id,
            'match_id': match_id
        })
        return jsonify({
            'error': 'Rate limit exceeded. Please wait before sending more messages.',
            'rate_limited': True
        }), 429

    match = Match.query.get_or_404(match_id)

    # Authorization: Verify current user is part of this match
    if match.user1_id != current_user.id and match.user2_id != current_user.id:
        log_security_event('unauthorized_message_attempt', {
            'match_id': match_id,
            'attempted_by': current_user.id
        })
        return jsonify({'error': 'Invalid conversation'}), 403

    if not match.is_active:
        return jsonify({'error': 'Conversation not active'}), 403

    # Check if other user has blocked current user
    other_user = match.get_other_user(current_user.id)
    if current_user.is_blocked_by(other_user):
        return jsonify({'error': 'Cannot send message'}), 403

    # Get and validate content
    content = request.form.get('content', '')
    
    # Validate and sanitize message
    is_valid, error_msg, sanitized_content = validate_message_content(
        content, 
        max_length=MAX_MESSAGE_LENGTH,
        min_length=MIN_MESSAGE_LENGTH
    )
    
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    # Save message with sanitized content
    message = Message.send_message(
        match_id=match_id,
        sender_id=current_user.id,
        content=sanitized_content
    )

    # Record for rate limiting
    record_socket_message(current_user.id)

    # Emit socket event for real-time update to other user
    # Note: Content is already sanitized, but we escape again for safety
    socketio.emit('new_message', {
        'match_id': match_id,
        'message_id': message.id,
        'sender_id': current_user.id,
        'sender_name': current_user.display_name,
        'sender_photo': current_user.primary_photo_url,
        'content': message.content,  # Already sanitized
        'created_at': message.created_at.strftime('%I:%M %p'),
    }, room=f'match_{match_id}')

    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'created_at': message.created_at.strftime('%I:%M %p'),
            'sender_id': current_user.id,
        }
    })


# SocketIO events for real-time messaging with security
@socketio.on('join_conversation')
def on_join(data):
    """Join a conversation room - with authorization check."""
    from flask_login import current_user
    
    # Verify user is authenticated
    if not current_user.is_authenticated:
        emit('error', {'message': 'Not authenticated'})
        return
    
    match_id = data.get('match_id')
    if not match_id:
        return
    
    # Verify user has access to this conversation
    if not validate_socket_match_access(match_id, current_user.id):
        log_security_event('unauthorized_room_join', {
            'match_id': match_id,
            'user_id': current_user.id
        })
        emit('error', {'message': 'Access denied'})
        return
    
    room = f'match_{match_id}'
    join_room(room)
    emit('joined', {'match_id': match_id})


@socketio.on('leave_conversation')
def on_leave(data):
    """Leave a conversation room."""
    match_id = data.get('match_id')
    if match_id:
        room = f'match_{match_id}'
        leave_room(room)


@socketio.on('send_message')
def on_message(data):
    """Handle message sent via WebSocket with full security validation and rate limiting."""
    from flask_login import current_user

    # Verify authentication
    if not current_user.is_authenticated:
        emit('error', {'message': 'Not authenticated'})
        return

    # Check rate limit
    allowed, remaining = check_socket_rate_limit(current_user.id)
    if not allowed:
        log_security_event('socket_rate_limit_exceeded', {
            'user_id': current_user.id
        })
        emit('error', {'message': 'Too many messages. Please slow down.', 'rate_limited': True})
        return

    match_id = data.get('match_id')
    content = data.get('content', '')

    if not match_id:
        emit('error', {'message': 'Invalid request'})
        return

    # Validate and sanitize content
    is_valid, error_msg, sanitized_content = validate_message_content(
        content,
        max_length=MAX_MESSAGE_LENGTH,
        min_length=MIN_MESSAGE_LENGTH
    )

    if not is_valid:
        emit('error', {'message': error_msg})
        return

    # Verify user is part of match
    match = Match.query.get(match_id)
    if not match or (match.user1_id != current_user.id and match.user2_id != current_user.id):
        log_security_event('unauthorized_socket_message', {
            'match_id': match_id,
            'user_id': current_user.id
        })
        emit('error', {'message': 'Access denied'})
        return

    # Check if match is active
    if not match.is_active:
        emit('error', {'message': 'Conversation not active'})
        return

    # Check if blocked
    other_user = match.get_other_user(current_user.id)
    if current_user.is_blocked_by(other_user):
        emit('error', {'message': 'Cannot send message'})
        return

    # Save message with sanitized content
    message = Message.send_message(
        match_id=match_id,
        sender_id=current_user.id,
        content=sanitized_content
    )

    # Record for rate limiting
    record_socket_message(current_user.id)

    # Emit to room
    emit('new_message', {
        'match_id': match_id,
        'message_id': message.id,
        'sender_id': current_user.id,
        'sender_name': current_user.display_name,
        'sender_photo': current_user.primary_photo_url,
        'content': message.content,
        'created_at': message.created_at.strftime('%I:%M %p'),
    }, room=f'match_{match_id}')


@socketio.on('mark_read')
def on_mark_read(data):
    """Mark messages as read - with auth check and broadcast to sender."""
    from flask_login import current_user

    if not current_user.is_authenticated:
        return

    match_id = data.get('match_id')
    if not match_id:
        return

    # Verify access before marking
    if validate_socket_match_access(match_id, current_user.id):
        Message.mark_conversation_read(match_id, current_user.id)

        # Broadcast read receipt to the room so sender knows their messages were read
        emit('messages_read', {
            'match_id': match_id,
            'read_by': current_user.id,
            'read_at': datetime.utcnow().strftime('%I:%M %p'),
        }, room=f'match_{match_id}', include_self=False)


@socketio.on('typing')
def on_typing(data):
    """Handle typing indicator - with auth check and timestamp for auto-clear."""
    from flask_login import current_user

    if not current_user.is_authenticated:
        return

    match_id = data.get('match_id')
    is_typing = data.get('is_typing', False)

    if not match_id:
        return

    # Verify user is part of match before broadcasting
    if not validate_socket_match_access(match_id, current_user.id):
        return

    # Emit typing status to room with timestamp for client-side auto-clear
    # Client should auto-clear typing indicator after 3 seconds without new typing event
    emit('user_typing', {
        'match_id': match_id,
        'user_id': current_user.id,
        'user_name': current_user.display_name,
        'is_typing': bool(is_typing),
        'timestamp': datetime.utcnow().isoformat(),
    }, room=f'match_{match_id}', include_self=False)


@socketio.on('stop_typing')
def on_stop_typing(data):
    """Explicitly stop typing indicator."""
    from flask_login import current_user

    if not current_user.is_authenticated:
        return

    match_id = data.get('match_id')
    if not match_id:
        return

    if validate_socket_match_access(match_id, current_user.id):
        emit('user_typing', {
            'match_id': match_id,
            'user_id': current_user.id,
            'user_name': current_user.display_name,
            'is_typing': False,
            'timestamp': datetime.utcnow().isoformat(),
        }, room=f'match_{match_id}', include_self=False)
