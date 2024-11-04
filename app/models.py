from . import db
from passlib.hash import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, first_name, last_name, phone, user_type, password):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.user_type = user_type
        # Hash the password before storing it in the database using bcrypt
        self.password = bcrypt.hash(password)

    def verify_password(self, password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.verify(password, self.password)
