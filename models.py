from flask_sqlalchemy import SQLAlchemy

# Instantiate SQLAlchemy to manage database interactions.
db = SQLAlchemy()


class User(db.Model):
    """
    User model for storing Pronote credentials.

    Attributes:
        id (int): Primary key.
        pronote_username (str): The username for the Pronote portal.
        pronote_password (str): The password for the Pronote portal.
    """
    id = db.Column(db.Integer, primary_key=True)
    pronote_username = db.Column(db.String(64), nullable=False)
    pronote_password = db.Column(db.String(128), nullable=False)

    def __repr__(self) -> str:
        """
        Return a string representation of the User instance.

        Returns:
            str: A string showing the user's pronote_username.
        """
        return f"<User {self.pronote_username}>"
