from . import db
from passlib.hash import bcrypt
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Define a relationship with the Ride table
    rides = db.relationship('Ride', backref='user', lazy=True)

    def __init__(self, username, first_name='', last_name='', phone='', user_type='', password='', id=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.user_type = user_type
        self.password = bcrypt.hash(password)  # Store the hashed password

    def verify_password(self, password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.verify(password, self.password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Ride(db.Model):
    __tablename__ = 'rides'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to link to the User table
    date = db.Column(db.Date, nullable=False)  # Ride date
    time = db.Column(db.Time, nullable=False)  # Ride time
    ride_provider = db.Column(db.String(50), nullable=False)  # Ride provider name
    pickup_location = db.Column(db.String(500), nullable=False)  # Ride provider name
    drop_location = db.Column(db.String(500), nullable=False)  # Ride provider name
    ride_status = db.Column(db.String(20), nullable=False)  # Ride provider name
    insert_ts = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp for insertion
    updt_ts = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # Timestamp for updates

    def __init__(self, user_id, date, time, ride_provider,pickup_location,drop_location,ride_status):
        self.user_id = user_id
        self.date = date
        self.time = time
        self.ride_provider = ride_provider
        self.pickup_location = pickup_location
        self.drop_location = drop_location
        self.ride_status = ride_status
        self.insert_ts = datetime.utcnow()  # Default to current time if not provided

