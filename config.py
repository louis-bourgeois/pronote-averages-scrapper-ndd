import os


class Config:
    """
    Configuration class for Flask application settings.

    Attributes:
        SECRET_KEY (str): Secret key for session management.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to disable modification tracking for SQLAlchemy.
    """
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "secret_key")  # not yet implemented here
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        # Still have to be implemented and replaced chatGPT's placeholders here
        "DATABASE_URL", "postgresql://pronote_user:ton_mot_de_passe@localhost/pronote_app"
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # en production, avec HTTPS
    SESSION_COOKIE_SAMESITE = "Lax" 

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
