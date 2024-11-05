from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import User
from . import db
import firebase_admin
from firebase_admin import credentials, auth
from sqlalchemy import text  # Import the text function for raw SQL queries
from werkzeug.security import check_password_hash  # Import for password verification
from passlib.hash import bcrypt
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from .models import Ride

# Initialize Firebase Admin SDK
#cred = credentials.Certificate('ride-share.json')  # Replace with your actual path
#firebase_admin.initialize_app(cred)

main = Blueprint('main', __name__)

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('app.html'), 404

@main.route('/')
def home():
    if current_user.is_authenticated:
        # Redirect to the dashboard or another page if already logged in
        return redirect(url_for('main.dashboard'))  # Adjust 'main.dashboard' as needed
    else:
        return render_template('app.html')


@main.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        user_type = request.form['user_type']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate password match
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register.html'))  # Assuming there's a register route for the form page

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('register.html'))

        # Create a new user instance
        new_user = User(username, first_name, last_name, phone, user_type, password)

        # Add and commit the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.thank_you'))  # Use blueprint name
        #flash("Thanks for registering!")
    return render_template('register.html')



@main.route('/thank_you')
def thank_you():
    return "<h1>Thanks for registering!</h1>"

@main.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone_number = data.get('phone')

    try:
        # Send OTP using Firebase
        verification_id = auth.verify_phone_number(phone_number)
        return jsonify({'success': True, 'verificationId': verification_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp')
    verification_id = data.get('verificationId')

    try:
        # Verify OTP using Firebase
        auth.verify(verification_id, otp)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Use text() to wrap the raw SQL query
        user_data = db.session.execute(
            text("SELECT id, username, first_name, last_name, phone, user_type, password FROM users WHERE username = :username"),
            {'username': username}
        ).fetchone()

        if not user_data:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        # Check if user exists and verify password using passlib bcrypt
        if user_data and bcrypt.verify(password, user_data.password):
            # Create a User instance with the fetched data
            user = User(
                id=user_data.id,
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone,
                user_type=user_data.user_type,
                password=user_data.password,  # Use the hashed password
            )
            login_user(user)  # Log in the user
            return redirect(url_for('main.dashboard'))  # Redirect to a dashboard or home page
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

    return render_template('login.html')  # Render the login page again if not POST or on failure


@main.route('/dashboard')
@login_required
def dashboard():
    next_ride = Ride.query.filter_by(user_id=current_user.id).order_by(Ride.insert_ts.asc(), Ride.time.asc()).first()
    return render_template('user_home_page.html', next_ride=next_ride)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))


@main.route('/book-ride', methods=['GET', 'POST'])
@login_required
def book_ride():
    if request.method == 'POST':
        # Handle form submission
        date = request.form.get('date')
        time = request.form.get('time')

        if not date or not time:
            flash("Date and time must be selected!")
            return redirect(url_for('main.book_ride'))

        # Process the booking with the date and time...
        flash(f"Booking confirmed for {date} at {time}")
        return render_template('main.book_ride')

    # Generate the next three days
    today = datetime.now()
    dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]

    return render_template('book_ride.html', dates=dates)


@main.route('/history')
@login_required
def history():
    rides = Ride.query.filter_by(user_id=current_user.id).order_by(Ride.date.asc(),Ride.time.asc()).limit(10).all()
    # Redirect to the dashboard or another page if already logged in
    return render_template('ride_history.html', rides = rides) # Adjust 'main.dashboard' as needed


@main.route('/forgot-password')
def forgot_password():
    return render_template('login.html')


@main.route('/submit-ride', methods=['GET','POST'])
@login_required
def submit_ride():
    # Retrieve form data
    date = request.form['date']
    time = request.form['time']
    pickup_location = request.form['pickup_location']
    drop_location = request.form['drop_location']

    # Insert a new ride request with blank `ride_provider` and no initial update timestamp
    new_ride = Ride(
        user_id=current_user.id,
        date=date,
        time=time,
        ride_provider='',  # Set provider as blank for now
        pickup_location=pickup_location,
        drop_location=drop_location,
        ride_status = 'Pending',
    )

    # Add new ride request to the database
    db.session.add(new_ride)
    db.session.commit()

    # Confirmation flash message
    flash(f'Ride booked for {date} at {time}!', 'success')
    return redirect(url_for('main.dashboard'))



