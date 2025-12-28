"""Profile model for user dating profiles."""
from datetime import datetime
from app.extensions import db


class Profile(db.Model):
    """User dating profile with all personal information."""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Basic Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # 'male', 'female'
    
    # Location
    city = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    country = db.Column(db.String(10), default='US')  # 'US' or 'CA'
    
    # Romanian Heritage
    romanian_origin_region = db.Column(db.String(50))
    speaks_romanian = db.Column(db.String(20))  # 'fluent', 'conversational', 'learning', 'heritage'
    years_in_north_america = db.Column(db.Integer)
    
    # Faith & Religion
    denomination = db.Column(db.String(50), nullable=False)
    church_name = db.Column(db.String(100))
    church_attendance = db.Column(db.String(30))  # 'weekly', 'monthly', 'holidays', 'rarely'
    faith_importance = db.Column(db.String(20))  # 'very_important', 'important', 'somewhat'
    
    # About Me
    bio = db.Column(db.Text)
    occupation = db.Column(db.String(100))
    education = db.Column(db.String(50))  # 'high_school', 'bachelors', 'masters', 'doctorate'
    height_cm = db.Column(db.Integer)
    
    # Lifestyle
    has_children = db.Column(db.Boolean, default=False)
    wants_children = db.Column(db.String(20))  # 'yes', 'no', 'maybe', 'have_and_want_more'
    smoking = db.Column(db.String(20))  # 'never', 'occasionally', 'regularly'
    drinking = db.Column(db.String(20))  # 'never', 'socially', 'regularly'
    
    # Traditional/Conservative Values
    conservatism_level = db.Column(db.String(30))  # 'very_traditional', 'traditional', 'moderate', 'modern'
    head_covering = db.Column(db.String(30))  # For women: 'always_batic', 'church_batic', 'pamblica', 'sometimes', 'no'
    fasting_practice = db.Column(db.String(30))  # 'strict', 'most', 'some', 'rarely', 'no'
    prayer_frequency = db.Column(db.String(30))  # 'multiple_daily', 'daily', 'weekly', 'occasionally'
    bible_reading = db.Column(db.String(30))  # 'daily', 'weekly', 'monthly', 'occasionally'
    dietary_restrictions = db.Column(db.String(30))  # 'strict_orthodox', 'no_pork', 'vegetarian', etc.
    family_role_view = db.Column(db.String(30))  # 'traditional', 'complementarian', 'egalitarian', 'flexible'
    
    # Additional preferences
    wants_spouse_same_denomination = db.Column(db.Boolean, default=False)
    willing_to_relocate = db.Column(db.Boolean, default=False)
    wants_church_wedding = db.Column(db.Boolean, default=True)
    
    # What I'm Looking For
    looking_for_gender = db.Column(db.String(20))
    looking_for_age_min = db.Column(db.Integer, default=18)
    looking_for_age_max = db.Column(db.Integer, default=99)
    relationship_goal = db.Column(db.String(30))  # 'marriage', 'serious', 'friendship_first'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = datetime.today()
            born = self.date_of_birth
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None
    
    @property
    def location_display(self):
        """Get formatted location string."""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.state_province:
            parts.append(self.state_province)
        if self.country:
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Location not specified'
    
    @property
    def height_display(self):
        """Get formatted height string."""
        if not self.height_cm:
            return None
        # Convert to feet and inches
        total_inches = self.height_cm / 2.54
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        return f"{feet}'{inches}\" ({self.height_cm} cm)"
    
    @property
    def is_complete(self):
        """Check if profile has minimum required fields."""
        required_fields = [
            self.first_name,
            self.date_of_birth,
            self.gender,
            self.denomination,
            self.bio,
            self.city,
            self.looking_for_gender,
        ]
        return all(required_fields)
    
    @property
    def completion_percentage(self):
        """Calculate profile completion percentage."""
        fields = [
            self.first_name, self.date_of_birth, self.gender,
            self.city, self.state_province, self.country,
            self.romanian_origin_region, self.speaks_romanian,
            self.denomination, self.church_attendance, self.faith_importance,
            self.bio, self.occupation, self.education, self.height_cm,
            self.looking_for_gender, self.relationship_goal,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)
    
    def matches_preferences(self, other_user):
        """Check if another user matches this user's preferences."""
        if not other_user.profile:
            return False
        
        other_profile = other_user.profile
        
        # Check gender preference
        if self.looking_for_gender and other_profile.gender != self.looking_for_gender:
            return False
        
        # Check age range
        other_age = other_profile.age
        if other_age:
            if self.looking_for_age_min and other_age < self.looking_for_age_min:
                return False
            if self.looking_for_age_max and other_age > self.looking_for_age_max:
                return False
        
        return True
    
    # Display helpers for template rendering
    GENDER_DISPLAY = {
        'male': 'Male',
        'female': 'Female',
    }
    
    SPEAKS_ROMANIAN_DISPLAY = {
        'fluent': 'Fluent',
        'conversational': 'Conversational',
        'learning': 'Learning',
        'heritage': 'Heritage Speaker',
    }
    
    CHURCH_ATTENDANCE_DISPLAY = {
        'weekly': 'Every Week',
        'monthly': 'Monthly',
        'holidays': 'Major Holidays',
        'rarely': 'Rarely',
    }
    
    FAITH_IMPORTANCE_DISPLAY = {
        'very_important': 'Very Important',
        'important': 'Important',
        'somewhat': 'Somewhat Important',
    }
    
    EDUCATION_DISPLAY = {
        'high_school': 'High School',
        'some_college': 'Some College',
        'bachelors': "Bachelor's Degree",
        'masters': "Master's Degree",
        'doctorate': 'Doctorate',
    }
    
    WANTS_CHILDREN_DISPLAY = {
        'yes': 'Yes',
        'no': 'No',
        'maybe': 'Maybe',
        'have_and_want_more': 'Have kids, want more',
    }
    
    RELATIONSHIP_GOAL_DISPLAY = {
        'marriage': 'Marriage',
        'serious': 'Serious Relationship',
        'friendship_first': 'Friendship First',
    }
    
    CONSERVATISM_DISPLAY = {
        'very_traditional': 'Very Traditional',
        'traditional': 'Traditional',
        'moderate': 'Moderate',
        'modern': 'Modern',
    }
    
    HEAD_COVERING_DISPLAY = {
        'always_batic': 'Always wear batic',
        'church_batic': 'Batic at church',
        'pamblica': 'Pamblica (headband)',
        'sometimes': 'Sometimes',
        'no': 'No head covering',
    }
    
    FASTING_DISPLAY = {
        'strict': 'Strict (all periods)',
        'most': 'Most fasting periods',
        'some': 'Some (major holidays)',
        'rarely': 'Rarely',
        'no': 'Do not fast',
    }
    
    PRAYER_DISPLAY = {
        'multiple_daily': 'Multiple times daily',
        'daily': 'Daily',
        'weekly': 'Weekly',
        'occasionally': 'Occasionally',
    }
    
    FAMILY_ROLE_DISPLAY = {
        'traditional': 'Traditional',
        'complementarian': 'Complementarian',
        'egalitarian': 'Egalitarian',
        'flexible': 'Flexible',
    }
    
    def get_gender_display(self):
        return self.GENDER_DISPLAY.get(self.gender, self.gender)
    
    def get_speaks_romanian_display(self):
        return self.SPEAKS_ROMANIAN_DISPLAY.get(self.speaks_romanian, self.speaks_romanian)
    
    def get_church_attendance_display(self):
        return self.CHURCH_ATTENDANCE_DISPLAY.get(self.church_attendance, self.church_attendance)
    
    def get_faith_importance_display(self):
        return self.FAITH_IMPORTANCE_DISPLAY.get(self.faith_importance, self.faith_importance)
    
    def get_education_display(self):
        return self.EDUCATION_DISPLAY.get(self.education, self.education)
    
    def get_wants_children_display(self):
        return self.WANTS_CHILDREN_DISPLAY.get(self.wants_children, self.wants_children)
    
    def get_relationship_goal_display(self):
        return self.RELATIONSHIP_GOAL_DISPLAY.get(self.relationship_goal, self.relationship_goal)
    
    def get_conservatism_display(self):
        return self.CONSERVATISM_DISPLAY.get(self.conservatism_level, self.conservatism_level)
    
    def get_head_covering_display(self):
        return self.HEAD_COVERING_DISPLAY.get(self.head_covering, self.head_covering)
    
    def get_fasting_display(self):
        return self.FASTING_DISPLAY.get(self.fasting_practice, self.fasting_practice)
    
    def get_prayer_display(self):
        return self.PRAYER_DISPLAY.get(self.prayer_frequency, self.prayer_frequency)
    
    def get_family_role_display(self):
        return self.FAMILY_ROLE_DISPLAY.get(self.family_role_view, self.family_role_view)
    
    def __repr__(self):
        return f'<Profile {self.first_name} ({self.user_id})>'

