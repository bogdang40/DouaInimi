"""Application configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    APP_NAME = os.environ.get('APP_NAME', 'Două Inimi')
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5001')
    
    # Conservatism levels
    CONSERVATISM_LEVELS = [
        ('very_traditional', 'Very Traditional'),
        ('traditional', 'Traditional'),
        ('moderate', 'Moderate'),
        ('modern', 'Modern'),
    ]
    
    # Head covering options (for women)
    HEAD_COVERING_OPTIONS = [
        ('always_batic', 'Always wear batic (headscarf)'),
        ('church_batic', 'Batic at church only'),
        ('pamblica', 'Pamblica (headband)'),
        ('sometimes', 'Sometimes'),
        ('no', 'No head covering'),
    ]
    
    # Fasting practices
    FASTING_OPTIONS = [
        ('strict', 'Strict fasting (all fasting periods)'),
        ('most', 'Most fasting periods'),
        ('some', 'Some fasting (major holidays)'),
        ('rarely', 'Rarely'),
        ('no', 'Do not fast'),
    ]
    
    # Prayer frequency
    PRAYER_OPTIONS = [
        ('multiple_daily', 'Multiple times daily'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('occasionally', 'Occasionally'),
    ]
    
    # Bible reading
    BIBLE_READING_OPTIONS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('occasionally', 'Occasionally'),
    ]
    
    # Dietary restrictions
    DIETARY_OPTIONS = [
        ('strict_orthodox', 'Strict Orthodox (no pork, fasting rules)'),
        ('no_pork', 'No pork'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('no_restrictions', 'No restrictions'),
    ]
    
    # Family values
    FAMILY_ROLES = [
        ('traditional', 'Traditional (husband leads, wife homemaker)'),
        ('complementarian', 'Complementarian (distinct but equal roles)'),
        ('egalitarian', 'Egalitarian (shared responsibilities)'),
        ('flexible', 'Flexible / Open to discussion'),
    ]
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dating.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    UPLOAD_FOLDER = 'uploads'
    
    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'photos')
    
    # Email (SendGrid)
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_FROM', 'noreply@yourapp.com')
    
    # App Settings
    USERS_PER_PAGE = 20
    MESSAGES_PER_PAGE = 50
    MAX_PHOTOS_PER_USER = 6
    
    # reCAPTCHA (get keys from https://www.google.com/recaptcha/admin)
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_TYPE = os.environ.get('RECAPTCHA_TYPE', 'v2')  # 'v2' or 'v3'
    RECAPTCHA_SCORE_THRESHOLD = 0.5  # For v3 only
    
    # Moderation
    ENABLE_AUTO_MODERATION = True
    MODERATION_ACTION_ON_FLAG = 'flag_for_review'  # 'none', 'flag_for_review', 'suspend'
    
    # Romanian Denominations
    DENOMINATIONS = [
        ('orthodox', 'Orthodox Christian'),
        ('greek_catholic', 'Greek Catholic (Byzantine)'),
        ('roman_catholic', 'Roman Catholic'),
        ('baptist', 'Baptist'),
        ('pentecostal', 'Pentecostal'),
        ('evangelical', 'Evangelical'),
        ('adventist', 'Seventh-day Adventist'),
        ('lutheran', 'Lutheran'),
        ('reformed', 'Reformed/Presbyterian'),
        ('non_denominational', 'Non-denominational'),
        ('other', 'Other Christian'),
    ]
    
    # Romanian Regions
    ROMANIAN_REGIONS = [
        ('transilvania', 'Transilvania'),
        ('moldova', 'Moldova'),
        ('muntenia', 'Muntenia (Wallachia)'),
        ('oltenia', 'Oltenia'),
        ('dobrogea', 'Dobrogea'),
        ('banat', 'Banat'),
        ('crisana', 'Crișana'),
        ('maramures', 'Maramureș'),
        ('bucovina', 'Bucovina'),
        ('other', 'Other / Multiple'),
    ]
    
    # US States and Canadian Provinces
    US_STATES = [
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
        ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
        ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
        ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'Washington D.C.'),
    ]
    
    CA_PROVINCES = [
        ('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'), ('NL', 'Newfoundland and Labrador'),
        ('NS', 'Nova Scotia'), ('NT', 'Northwest Territories'), ('NU', 'Nunavut'),
        ('ON', 'Ontario'), ('PE', 'Prince Edward Island'), ('QC', 'Quebec'),
        ('SK', 'Saskatchewan'), ('YT', 'Yukon'),
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dating_dev.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Override with production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}

