"""Message and report forms."""
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class MessageForm(FlaskForm):
    """Message send form."""
    content = TextAreaField('Message', validators=[
        DataRequired(message='Please enter a message'),
        Length(min=1, max=5000, message='Message must be between 1 and 5000 characters')
    ])
    submit = SubmitField('Send')


class ReportForm(FlaskForm):
    """Report user form."""
    reason = SelectField('Reason', choices=[
        ('', 'Select a reason'),
        ('fake_profile', 'Fake Profile'),
        ('inappropriate_photos', 'Inappropriate Photos'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('underage', 'Appears Underage'),
        ('scam', 'Scam/Fraud'),
        ('other', 'Other'),
    ], validators=[DataRequired(message='Please select a reason')])
    
    details = TextAreaField('Additional Details', validators=[
        Optional(),
        Length(max=2000)
    ])
    
    submit = SubmitField('Submit Report')

