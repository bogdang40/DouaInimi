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

    # Church Attire & Modesty (Orthodox-specific)
    church_attire_women = db.Column(db.String(30))  # 'skirt_dress_only', 'modest_pants_ok', 'flexible'
    modesty_level = db.Column(db.String(30))  # 'very_modest', 'modest', 'moderate', 'flexible'

    # Orthodox Sacraments & Practices
    confession_frequency = db.Column(db.String(30))  # 'regularly', 'before_communion', 'annually', 'major_feasts', 'rarely'
    communion_frequency = db.Column(db.String(30))  # 'weekly', 'monthly', 'major_feasts', 'annually', 'rarely'
    icons_in_home = db.Column(db.Boolean, default=True)  # Orthodox iconostasis/prayer corner
    saints_nameday = db.Column(db.String(100))  # Patron saint name

    # Marital History (important for Orthodox wedding rules)
    marital_history = db.Column(db.String(30))  # 'never_married', 'divorced_civil', 'divorced_church', 'widowed', 'annulled'

    # Family Planning
    desired_children_count = db.Column(db.String(20))  # '1-2', '3-4', '5+', 'as_god_wills', 'none'
    children_education_preference = db.Column(db.String(50))  # 'orthodox_school', 'private_christian', 'homeschool', 'public', 'flexible'

    # Additional preferences
    wants_spouse_same_denomination = db.Column(db.Boolean, default=False)
    willing_to_relocate = db.Column(db.Boolean, default=False)
    wants_church_wedding = db.Column(db.Boolean, default=True)
    seeks_modest_spouse = db.Column(db.Boolean, default=False)  # Looking for modest partner
    
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

    CHURCH_ATTIRE_DISPLAY = {
        'skirt_dress_only': 'Skirt/Dress Only',
        'modest_pants_ok': 'Modest Pants Okay',
        'flexible': 'Flexible',
    }

    MODESTY_DISPLAY = {
        'very_modest': 'Very Modest',
        'modest': 'Modest',
        'moderate': 'Moderate',
        'flexible': 'Flexible',
    }

    CONFESSION_DISPLAY = {
        'regularly': 'Regularly (monthly+)',
        'before_communion': 'Before Communion',
        'annually': 'Annually (Great Lent)',
        'major_feasts': 'Major Feasts',
        'rarely': 'Rarely',
    }

    COMMUNION_DISPLAY = {
        'weekly': 'Weekly',
        'monthly': 'Monthly',
        'major_feasts': 'Major Feasts Only',
        'annually': 'Annually',
        'rarely': 'Rarely',
    }

    MARITAL_HISTORY_DISPLAY = {
        'never_married': 'Never Married',
        'divorced_civil': 'Divorced (Civil)',
        'divorced_church': 'Divorced (Church)',
        'widowed': 'Widowed',
        'annulled': 'Annulled',
    }

    DESIRED_CHILDREN_DISPLAY = {
        '1-2': '1-2 Children',
        '3-4': '3-4 Children',
        '5+': '5+ Children',
        'as_god_wills': 'As God Wills',
        'none': 'No Children',
    }

    CHILDREN_EDUCATION_DISPLAY = {
        'orthodox_school': 'Orthodox School',
        'private_christian': 'Private Christian School',
        'homeschool': 'Homeschool',
        'public': 'Public School',
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

    def get_church_attire_display(self):
        return self.CHURCH_ATTIRE_DISPLAY.get(self.church_attire_women, self.church_attire_women)

    def get_modesty_display(self):
        return self.MODESTY_DISPLAY.get(self.modesty_level, self.modesty_level)

    def get_confession_display(self):
        return self.CONFESSION_DISPLAY.get(self.confession_frequency, self.confession_frequency)

    def get_communion_display(self):
        return self.COMMUNION_DISPLAY.get(self.communion_frequency, self.communion_frequency)

    def get_marital_history_display(self):
        return self.MARITAL_HISTORY_DISPLAY.get(self.marital_history, self.marital_history)

    def get_desired_children_display(self):
        return self.DESIRED_CHILDREN_DISPLAY.get(self.desired_children_count, self.desired_children_count)

    def get_children_education_display(self):
        return self.CHILDREN_EDUCATION_DISPLAY.get(self.children_education_preference, self.children_education_preference)

    def calculate_compatibility(self, other_profile):
        """Calculate compatibility score with another profile (0-100)."""
        if not other_profile:
            return 0

        score = 0
        total_weight = 0

        # Denomination match (weight: 20)
        if self.denomination and other_profile.denomination:
            total_weight += 20
            if self.denomination == other_profile.denomination:
                score += 20
            elif self.wants_spouse_same_denomination:
                score += 0  # Must match if required
            else:
                score += 10  # Partial credit for different denominations

        # Conservatism alignment (weight: 15)
        conservatism_order = ['very_traditional', 'traditional', 'moderate', 'modern']
        if self.conservatism_level and other_profile.conservatism_level:
            total_weight += 15
            try:
                diff = abs(conservatism_order.index(self.conservatism_level) -
                          conservatism_order.index(other_profile.conservatism_level))
                score += max(0, 15 - (diff * 5))
            except ValueError:
                pass

        # Fasting practice alignment (weight: 10)
        fasting_order = ['strict', 'most', 'some', 'rarely', 'no']
        if self.fasting_practice and other_profile.fasting_practice:
            total_weight += 10
            try:
                diff = abs(fasting_order.index(self.fasting_practice) -
                          fasting_order.index(other_profile.fasting_practice))
                score += max(0, 10 - (diff * 2))
            except ValueError:
                pass

        # Prayer frequency alignment (weight: 10)
        prayer_order = ['multiple_daily', 'daily', 'weekly', 'occasionally']
        if self.prayer_frequency and other_profile.prayer_frequency:
            total_weight += 10
            try:
                diff = abs(prayer_order.index(self.prayer_frequency) -
                          prayer_order.index(other_profile.prayer_frequency))
                score += max(0, 10 - (diff * 3))
            except ValueError:
                pass

        # Family role view (weight: 15)
        if self.family_role_view and other_profile.family_role_view:
            total_weight += 15
            if self.family_role_view == other_profile.family_role_view:
                score += 15
            elif self.family_role_view in ['traditional', 'complementarian'] and \
                 other_profile.family_role_view in ['traditional', 'complementarian']:
                score += 12
            elif 'flexible' in [self.family_role_view, other_profile.family_role_view]:
                score += 10
            else:
                score += 5

        # Modesty alignment (weight: 10)
        modesty_order = ['very_modest', 'modest', 'moderate', 'flexible']
        if self.modesty_level and other_profile.modesty_level:
            total_weight += 10
            try:
                diff = abs(modesty_order.index(self.modesty_level) -
                          modesty_order.index(other_profile.modesty_level))
                score += max(0, 10 - (diff * 3))
            except ValueError:
                pass

        # Children preference (weight: 10)
        if self.wants_children and other_profile.wants_children:
            total_weight += 10
            if self.wants_children == other_profile.wants_children:
                score += 10
            elif self.wants_children in ['yes', 'maybe'] and other_profile.wants_children in ['yes', 'maybe']:
                score += 7
            else:
                score += 3

        # Church attendance (weight: 10)
        attendance_order = ['weekly', 'monthly', 'holidays', 'rarely']
        if self.church_attendance and other_profile.church_attendance:
            total_weight += 10
            try:
                diff = abs(attendance_order.index(self.church_attendance) -
                          attendance_order.index(other_profile.church_attendance))
                score += max(0, 10 - (diff * 3))
            except ValueError:
                pass

        # Calculate percentage
        if total_weight == 0:
            return 50  # Default if no comparable fields

        return int((score / total_weight) * 100)

    def __repr__(self):
        return f'<Profile {self.first_name} ({self.user_id})>'

