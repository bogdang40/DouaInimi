"""Profile forms."""
from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, SelectField, IntegerField, 
                     BooleanField, DateField, SubmitField)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from flask import current_app


class ProfileForm(FlaskForm):
    """Main profile edit form."""
    
    # Basic Info
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        Optional(),
        Length(max=50)
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(message='Date of birth is required')
    ])
    gender = SelectField('Gender', choices=[
        ('', 'Select your gender'),
        ('male', 'Male'),
        ('female', 'Female'),
    ], validators=[DataRequired(message='Please select your gender')])
    
    # Location
    city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(max=100)
    ])
    state_province = SelectField('State/Province', validators=[
        DataRequired(message='Please select your state/province')
    ])
    country = SelectField('Country', choices=[
        ('US', 'United States'),
        ('CA', 'Canada'),
    ], validators=[DataRequired()])
    
    # Romanian Heritage
    romanian_origin_region = SelectField('Region of Origin in Romania', validators=[Optional()])
    speaks_romanian = SelectField('Romanian Language Ability', choices=[
        ('', 'Select your level'),
        ('fluent', 'Fluent'),
        ('conversational', 'Conversational'),
        ('learning', 'Learning'),
        ('heritage', 'Heritage Speaker (understand but limited speaking)'),
    ], validators=[Optional()])
    years_in_north_america = IntegerField('Years in North America', validators=[
        Optional(),
        NumberRange(min=0, max=100)
    ])
    
    # Faith
    denomination = SelectField('Denomination', validators=[
        DataRequired(message='Please select your denomination')
    ])
    church_name = StringField('Church Name (Optional)', validators=[
        Optional(),
        Length(max=100)
    ])
    church_attendance = SelectField('Church Attendance', choices=[
        ('', 'How often do you attend?'),
        ('weekly', 'Every Week'),
        ('monthly', 'Monthly'),
        ('holidays', 'Major Holidays'),
        ('rarely', 'Rarely'),
    ], validators=[Optional()])
    faith_importance = SelectField('Importance of Faith', choices=[
        ('', 'How important is faith to you?'),
        ('very_important', 'Very Important'),
        ('important', 'Important'),
        ('somewhat', 'Somewhat Important'),
    ], validators=[Optional()])
    
    # About Me
    bio = TextAreaField('About Me', validators=[
        DataRequired(message='Please write something about yourself'),
        Length(min=50, max=2000, message='Bio must be between 50 and 2000 characters')
    ])
    occupation = StringField('Occupation', validators=[
        Optional(),
        Length(max=100)
    ])
    education = SelectField('Education', choices=[
        ('', 'Select your education level'),
        ('high_school', 'High School'),
        ('some_college', 'Some College'),
        ('bachelors', "Bachelor's Degree"),
        ('masters', "Master's Degree"),
        ('doctorate', 'Doctorate'),
    ], validators=[Optional()])
    height_cm = IntegerField('Height (cm)', validators=[
        Optional(),
        NumberRange(min=120, max=250, message='Please enter a valid height')
    ])
    height_ft = SelectField('Height (feet)', choices=[
        ('', 'Feet'),
        ('4', "4'"),
        ('5', "5'"),
        ('6', "6'"),
        ('7', "7'"),
    ], validators=[Optional()])
    height_in = SelectField('Height (inches)', choices=[
        ('', 'Inches'),
        ('0', '0"'),
        ('1', '1"'),
        ('2', '2"'),
        ('3', '3"'),
        ('4', '4"'),
        ('5', '5"'),
        ('6', '6"'),
        ('7', '7"'),
        ('8', '8"'),
        ('9', '9"'),
        ('10', '10"'),
        ('11', '11"'),
    ], validators=[Optional()])
    
    # Lifestyle
    has_children = BooleanField('I have children')
    wants_children = SelectField('Want Children?', choices=[
        ('', 'Do you want children?'),
        ('yes', 'Yes'),
        ('no', 'No'),
        ('maybe', 'Maybe'),
        ('have_and_want_more', 'Have kids, want more'),
    ], validators=[Optional()])
    smoking = SelectField('Smoking', choices=[
        ('', 'Do you smoke?'),
        ('never', 'Never'),
        ('occasionally', 'Occasionally'),
        ('regularly', 'Regularly'),
    ], validators=[Optional()])
    drinking = SelectField('Drinking', choices=[
        ('', 'Do you drink?'),
        ('never', 'Never'),
        ('socially', 'Socially'),
        ('regularly', 'Regularly'),
    ], validators=[Optional()])
    
    # Traditional/Conservative Values
    conservatism_level = SelectField('How Traditional Are You?', validators=[Optional()])
    head_covering = SelectField('Head Covering (Women)', validators=[Optional()])
    fasting_practice = SelectField('Fasting Practice', validators=[Optional()])
    prayer_frequency = SelectField('Prayer Frequency', validators=[Optional()])
    bible_reading = SelectField('Bible/Scripture Reading', validators=[Optional()])
    dietary_restrictions = SelectField('Dietary Practices', validators=[Optional()])
    family_role_view = SelectField('View on Family Roles', validators=[Optional()])
    
    # Additional preferences
    wants_spouse_same_denomination = BooleanField('I prefer a spouse from the same denomination')
    willing_to_relocate = BooleanField('I am willing to relocate for the right person')
    wants_church_wedding = BooleanField('I want a church wedding')
    
    # What I'm Looking For
    looking_for_gender = SelectField('Looking For', choices=[
        ('', 'Who are you looking for?'),
        ('male', 'Men'),
        ('female', 'Women'),
    ], validators=[DataRequired(message='Please specify who you are looking for')])
    looking_for_age_min = IntegerField('Minimum Age', validators=[
        Optional(),
        NumberRange(min=18, max=99)
    ], default=18)
    looking_for_age_max = IntegerField('Maximum Age', validators=[
        Optional(),
        NumberRange(min=18, max=99)
    ], default=99)
    relationship_goal = SelectField('Relationship Goal', choices=[
        ('', 'What are you looking for?'),
        ('marriage', 'Marriage'),
        ('serious', 'Serious Relationship'),
        ('friendship_first', 'Friendship First'),
    ], validators=[Optional()])
    
    submit = SubmitField('Save Profile')
    
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Populate dynamic choices
        self.denomination.choices = [('', 'Select your denomination')] + current_app.config['DENOMINATIONS']
        self.romanian_origin_region.choices = [('', 'Select region')] + current_app.config['ROMANIAN_REGIONS']
        self.state_province.choices = [('', 'Select state/province')] + current_app.config['US_STATES'] + current_app.config['CA_PROVINCES']
        
        # Traditional values choices
        self.conservatism_level.choices = [('', 'Select your level')] + current_app.config['CONSERVATISM_LEVELS']
        self.head_covering.choices = [('', 'Select option')] + current_app.config['HEAD_COVERING_OPTIONS']
        self.fasting_practice.choices = [('', 'Select your practice')] + current_app.config['FASTING_OPTIONS']
        self.prayer_frequency.choices = [('', 'How often do you pray?')] + current_app.config['PRAYER_OPTIONS']
        self.bible_reading.choices = [('', 'How often?')] + current_app.config['BIBLE_READING_OPTIONS']
        self.dietary_restrictions.choices = [('', 'Select your diet')] + current_app.config['DIETARY_OPTIONS']
        self.family_role_view.choices = [('', 'Select your view')] + current_app.config['FAMILY_ROLES']
    
    def validate_date_of_birth(self, field):
        """Ensure user is at least 18 years old."""
        if field.data:
            today = date.today()
            age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
            if age < 18:
                raise ValidationError('You must be at least 18 years old to use this service')
            if age > 120:
                raise ValidationError('Please enter a valid date of birth')


class PhotoUploadForm(FlaskForm):
    """Photo upload form."""
    photo = FileField('Upload Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Upload')


class PreferencesForm(FlaskForm):
    """Match preferences form."""
    looking_for_gender = SelectField('Looking For', choices=[
        ('male', 'Men'),
        ('female', 'Women'),
    ], validators=[DataRequired()])
    looking_for_age_min = IntegerField('Minimum Age', validators=[
        DataRequired(),
        NumberRange(min=18, max=99)
    ])
    looking_for_age_max = IntegerField('Maximum Age', validators=[
        DataRequired(),
        NumberRange(min=18, max=99)
    ])
    relationship_goal = SelectField('Relationship Goal', choices=[
        ('', 'Any'),
        ('marriage', 'Marriage'),
        ('serious', 'Serious Relationship'),
        ('friendship_first', 'Friendship First'),
    ], validators=[Optional()])
    submit = SubmitField('Save Preferences')

