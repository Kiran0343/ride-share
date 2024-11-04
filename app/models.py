from . import db
from passlib.hash import bcrypt
from flask_login import UserMixin  # Import UserMixin

class User(UserMixin, db.Model):  # Inherit from UserMixin
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, first_name='', last_name='', phone='', user_type='', password='', id=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.user_type = user_type
        self.password = password  # Store the hashed password later

    def verify_password(self, password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.verify(password, self.password)

    @property
    def is_active(self):
        return True  # Return True if the user is active

    @property
    def is_authenticated(self):
        return True  # Return True for authenticated users

    @property
    def is_anonymous(self):
        return False  # Return False for non-anonymous users