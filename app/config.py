import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-electrostock-12345')
    FLASK_RUN_PORT = int(os.getenv('PORT', 5000))
    STATIC_FOLDER = 'infrastructure/static'
    TEMPLATES_FOLDER = 'infrastructure/templates'

    # PostgreSQL configuration
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT', 5432))
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'electrostock')
    DATABASE_USER = os.getenv('DATABASE_USER', 'electrostock_user')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'electrostock_pass')

    # SQLAlchemy — built as a class attribute so Flask's from_object() can read it
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}"
        f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS / LocalStack configuration
    AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'ap-southeast-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'test')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'test')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure SECRET_KEY is set in production environment
    SECRET_KEY = os.getenv('SECRET_KEY', 'prod-fallback-secret-key-electrostock-98765')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
