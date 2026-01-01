"""Search and filter forms."""
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import Optional, NumberRange
from flask import current_app


class SearchForm(FlaskForm):
    """Search/filter form for discovering matches."""
    
    # Basic filters
    gender = SelectField('Gender', choices=[
        ('', 'Any'),
        ('male', 'Men'),
        ('female', 'Women'),
    ], validators=[Optional()])
    
    age_min = IntegerField('Min Age', validators=[
        Optional(),
        NumberRange(min=18, max=99)
    ], default=18)
    
    age_max = IntegerField('Max Age', validators=[
        Optional(),
        NumberRange(min=18, max=99)
    ], default=99)
    
    # Location
    country = SelectField('Country', choices=[
        ('', 'Any'),
        ('US', 'United States'),
        ('CA', 'Canada'),
    ], validators=[Optional()])
    
    state_province = SelectField('State/Province', validators=[Optional()])
    
    city = StringField('City', validators=[Optional()])
    
    # Faith
    denomination = SelectField('Denomination', validators=[Optional()])
    
    church_attendance = SelectField('Church Attendance', choices=[
        ('', 'Any'),
        ('weekly', 'Every Week'),
        ('monthly', 'Monthly'),
        ('holidays', 'Major Holidays'),
    ], validators=[Optional()])
    
    # Romanian Heritage
    romanian_origin_region = SelectField('Romanian Region', validators=[Optional()])
    
    speaks_romanian = SelectField('Romanian Language', choices=[
        ('', 'Any'),
        ('fluent', 'Fluent'),
        ('conversational', 'Conversational'),
        ('learning', 'Learning'),
        ('heritage', 'Heritage Speaker'),
    ], validators=[Optional()])
    
    # Relationship
    relationship_goal = SelectField('Looking For', choices=[
        ('', 'Any'),
        ('marriage', 'Marriage'),
        ('serious', 'Serious Relationship'),
        ('friendship_first', 'Friendship First'),
    ], validators=[Optional()])
    
    # Education & Career
    education = SelectField('Education', choices=[
        ('', 'Any'),
        ('high_school', 'High School'),
        ('some_college', 'Some College'),
        ('bachelors', "Bachelor's Degree"),
        ('masters', "Master's Degree"),
        ('doctorate', 'Doctorate'),
    ], validators=[Optional()])

    # Lifestyle
    has_children = SelectField('Has Children', choices=[
        ('', 'Any'),
        ('yes', 'Yes'),
        ('no', 'No'),
    ], validators=[Optional()])

    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # Populate dynamic choices
        self.denomination.choices = [('', 'Any')] + current_app.config['DENOMINATIONS']
        self.romanian_origin_region.choices = [('', 'Any')] + current_app.config['ROMANIAN_REGIONS']
        self.state_province.choices = [('', 'Any')] + current_app.config['US_STATES'] + current_app.config['CA_PROVINCES']

