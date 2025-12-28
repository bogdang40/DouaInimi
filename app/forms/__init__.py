"""Form definitions."""
from app.forms.auth import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.forms.profile import ProfileForm, PhotoUploadForm, PreferencesForm
from app.forms.search import SearchForm
from app.forms.messages import MessageForm, ReportForm

__all__ = [
    'LoginForm', 'RegisterForm', 'ForgotPasswordForm', 'ResetPasswordForm',
    'ProfileForm', 'PhotoUploadForm', 'PreferencesForm',
    'SearchForm',
    'MessageForm', 'ReportForm',
]

