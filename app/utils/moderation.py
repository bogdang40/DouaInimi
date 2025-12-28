"""Content moderation utilities for auto-flagging suspicious content."""
import re
from datetime import datetime


# Suspicious patterns
SPAM_PATTERNS = [
    r'(https?://\S+){2,}',  # Multiple URLs
    r'(whatsapp|telegram|signal|viber)\s*[:\s]*[\d\+\(\)]',  # Phone app + number
    r'(cash\s*app|venmo|paypal|zelle|bitcoin|crypto)',  # Payment/crypto
    r'make\s*\$?\d+.*per\s*(day|hour|week|month)',  # Get rich quick
    r'(visa|green\s*card|citizenship).*marriage',  # Immigration fraud
    r'(sugar\s*(daddy|mommy|baby))',  # Sugar relationships
    r'(\bescort\b|\bprostitu)',  # Explicit services
    r'(nigerian|prince|inheritance|lottery)\s*(money|winner)',  # Scam patterns
    r'(\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)',  # Phone numbers in bio
]

# Suspicious words (partial match)
SUSPICIOUS_WORDS = [
    'instagram', 'snapchat', 'kik', 'telegram', 'whatsapp',
    'onlyfans', 'fansly', 'cashapp', 'venmo', 'paypal',
    'bitcoin', 'crypto', 'invest', 'trading', 'forex',
    'escort', 'massage', 'sensual', 'intimate services',
    'visa', 'green card', 'citizenship', 'sponsor',
    'sugar daddy', 'sugar mommy', 'arrangement',
]

# Required for verification
MINIMUM_BIO_LENGTH = 20
MINIMUM_PHOTOS = 1


class ModerationResult:
    """Result of content moderation check."""
    
    def __init__(self):
        self.is_flagged = False
        self.flags = []
        self.severity = 'none'  # 'none', 'low', 'medium', 'high'
        self.auto_action = None  # 'none', 'flag_for_review', 'suspend'
    
    def add_flag(self, reason, severity='low'):
        self.is_flagged = True
        self.flags.append({
            'reason': reason,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Update overall severity
        severity_order = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        if severity_order.get(severity, 0) > severity_order.get(self.severity, 0):
            self.severity = severity
    
    def to_dict(self):
        return {
            'is_flagged': self.is_flagged,
            'flags': self.flags,
            'severity': self.severity,
            'auto_action': self.auto_action
        }


def moderate_text(text, field_name='content'):
    """
    Check text content for suspicious patterns.
    
    Args:
        text: Text to check
        field_name: Name of the field being checked (for reporting)
    
    Returns:
        ModerationResult
    """
    result = ModerationResult()
    
    if not text:
        return result
    
    text_lower = text.lower()
    
    # Check spam patterns
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            result.add_flag(f"Suspicious pattern in {field_name}: {pattern}", 'medium')
    
    # Check suspicious words
    for word in SUSPICIOUS_WORDS:
        if word in text_lower:
            result.add_flag(f"Suspicious word in {field_name}: '{word}'", 'low')
    
    # Check for excessive caps (shouting)
    if len(text) > 20:
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if caps_ratio > 0.5:
            result.add_flag(f"Excessive caps in {field_name}", 'low')
    
    # Check for repetitive characters
    if re.search(r'(.)\1{4,}', text):
        result.add_flag(f"Repetitive characters in {field_name}", 'low')
    
    # Determine auto-action based on severity
    if result.severity == 'high':
        result.auto_action = 'suspend'
    elif result.severity == 'medium':
        result.auto_action = 'flag_for_review'
    elif result.severity == 'low' and len(result.flags) >= 3:
        result.auto_action = 'flag_for_review'
    else:
        result.auto_action = 'none'
    
    return result


def moderate_profile(profile):
    """
    Moderate an entire profile.
    
    Args:
        profile: Profile model instance
    
    Returns:
        ModerationResult with combined flags
    """
    result = ModerationResult()
    
    # Check bio
    if profile.bio:
        bio_result = moderate_text(profile.bio, 'bio')
        for flag in bio_result.flags:
            result.add_flag(flag['reason'], flag['severity'])
    
    # Check if bio is too short
    if profile.bio and len(profile.bio.strip()) < MINIMUM_BIO_LENGTH:
        result.add_flag('Bio is very short', 'low')
    
    # Check occupation
    if profile.occupation:
        occ_result = moderate_text(profile.occupation, 'occupation')
        for flag in occ_result.flags:
            result.add_flag(flag['reason'], flag['severity'])
    
    # Check church name (unlikely spam, but check anyway)
    if profile.church_name:
        church_result = moderate_text(profile.church_name, 'church_name')
        for flag in church_result.flags:
            result.add_flag(flag['reason'], flag['severity'])
    
    # Determine final action
    if result.severity == 'high':
        result.auto_action = 'suspend'
    elif result.severity == 'medium' or len(result.flags) >= 3:
        result.auto_action = 'flag_for_review'
    else:
        result.auto_action = 'none'
    
    return result


def moderate_photo(photo_path):
    """
    Basic photo moderation (placeholder for more advanced checks).
    In production, this would use an image moderation API.
    
    Args:
        photo_path: Path to the photo file
    
    Returns:
        ModerationResult
    """
    result = ModerationResult()
    
    # Placeholder - in production, use Azure Content Moderator,
    # Google Cloud Vision, or AWS Rekognition
    
    # For now, just return clean
    return result


def check_profile_completeness(user):
    """
    Check if a profile meets minimum requirements for verification.
    
    Args:
        user: User model instance
    
    Returns:
        (is_complete, missing_items)
    """
    missing = []
    
    if not user.profile:
        return False, ['No profile created']
    
    profile = user.profile
    
    # Required fields
    if not profile.first_name:
        missing.append('First name')
    if not profile.date_of_birth:
        missing.append('Date of birth')
    if not profile.gender:
        missing.append('Gender')
    if not profile.city:
        missing.append('City')
    if not profile.country:
        missing.append('Country')
    if not profile.denomination:
        missing.append('Denomination')
    if not profile.bio or len(profile.bio.strip()) < MINIMUM_BIO_LENGTH:
        missing.append(f'Bio (minimum {MINIMUM_BIO_LENGTH} characters)')
    
    # Photos
    photo_count = len(user.photos) if user.photos else 0
    if photo_count < MINIMUM_PHOTOS:
        missing.append(f'At least {MINIMUM_PHOTOS} photo(s)')
    
    return len(missing) == 0, missing


def flag_user_for_review(user, reason, severity='medium'):
    """
    Flag a user for admin review.
    
    Args:
        user: User model instance
        reason: Reason for flagging
        severity: 'low', 'medium', 'high'
    """
    from app.extensions import db
    from app.models.report import Report
    
    # Create a system report
    report = Report(
        reporter_id=None,  # System-generated
        reported_id=user.id,
        reason='auto_moderation',
        description=f"Auto-flagged: {reason}",
        status='pending'
    )
    
    db.session.add(report)
    db.session.commit()
    
    return report

