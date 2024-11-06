from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify,session
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


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        user_type = request.form['user_type']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        #email = request.form['email']
        email = 'kiran.kancharla92@gmail.com'

        # Validate password match
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('main.register'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('main.register'))

        # Generate a random OTP
        otp = random.randint(100000, 999999)

        # Store user details in session temporarily
        session['user_data'] = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'user_type': user_type,
            'password': password,  # Ideally, you'd hash the password here
            'email': email,
            'otp': otp  # Store OTP in session for validation
        }

        # Send OTP to the user's email
        send_email(email, otp)

        # Redirect to OTP validation page
        return redirect(url_for('main.validate_otp'))

    return render_template('register.html')



@main.route('/thank_you')
def thank_you():
    return "<h1>Thanks for registering!</h1>"


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
    next_ride = Ride.query.filter_by(user_id=current_user.id).order_by(Ride.date.asc(), Ride.time.asc()).first()
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


@main.route('/submit-ride', methods=['GET','POST'])
@login_required
def submit_ride():
    if request.method == 'POST':
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
        #flash(f'Ride booked for {date} at {time}!', 'success')
        return redirect(url_for('main.history'))
    return redirect(url_for('main.dashboard'))



@main.route('/cancel_ride/<int:ride_id>', methods=['GET','POST'])
@login_required
def cancel_ride(ride_id):
    if request.method == 'POST':
        ride = Ride.query.get(ride_id)
        if ride:
             db.session.delete(ride)
             db.session.commit()
        return redirect(url_for('main.history'))
    return redirect(url_for('main.history'))


@main.route('/edit_ride/<int:ride_id>',methods=['GET','POST'])
@login_required
def edit_ride(ride_id):
    if request.method == 'POST':
        ride = Ride.query.get_or_404(ride_id)

        # Ensure user authorization
        if ride.user_id != current_user.id:
            flash("You are not authorized to edit this ride.", "danger")
            return redirect(url_for('main.history'))

        # Fetch dates for the dropdown
        today = datetime.now()
        dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]

        return render_template('book_ride.html', ride=ride, dates=dates)
    return redirect(url_for('main.history'))


@main.route('/update_ride/<int:ride_id>', methods=['GET','POST'])
@login_required
def update_ride(ride_id):
    if request.method == 'POST':
        # Fetch the ride from the database
        ride = Ride.query.get_or_404(ride_id)

        # Update the ride attributes based on form data
        ride.date = request.form['date']
        ride.time = request.form['time']
        ride.pickup_location = request.form['pickup_location']
        ride.drop_location = request.form['drop_location']
        # Save changes to the database
        db.session.commit()
        return redirect(url_for('main.history'))
    return redirect(url_for('main.history'))

@main.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)  # Get the current user's data
    return render_template('profile.html', user=user)


@main.route('/profile/update', methods=['GET','POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Get the form data
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')

        try:
            # Update current user's details
            current_user.username = username
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.phone = phone

            # Commit changes to the database
            db.session.commit()

            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            #flash(f'An error occurred while updating the profile: {str(e)}', 'error')

        # Redirect back to the profile page
        return redirect(url_for('main.profile'))
    return redirect(url_for('main.profile'))

import random
import smtplib
@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Generate a random OTP
        otp = random.randint(100000, 999999)

        # Send OTP to the email
        send_email(email, otp)

        return redirect(url_for('main.verify_otp'))

    return render_template('forgot_password.html')


def send_email(to_email, otp):
    # Gmail credentials
    from_email = 'kiranlk1989@gmail.com'
    from_password = 'uzxwsgfuohtzioyu'  # Use App Passwords if 2FA is enabled

    subject = 'Your OTP Code'
    body = f'Your OTP code is: {otp}'

    message = f'Subject: {subject}\n\n{body}'
    # Connect to Gmail SMTP server
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, message)


@main.route('/validate_otp', methods=['GET', 'POST'])
def validate_otp():
    stored_data = session.get('user_data')
    if not stored_data:
        flash("Session expired, please register again.")
        return redirect(url_for('main.register'))

    if request.method == 'POST':
        print (request.form)
        user_otp = ''.join([
            request.form.get('otp1'),
            request.form.get('otp2'),
            request.form.get('otp3'),
            request.form.get('otp4'),
            request.form.get('otp5'),
            request.form.get('otp6')
        ])
        print (user_otp)
        print (str(stored_data['otp']))
        if str(stored_data['otp']) == user_otp:
            # Create a new user instance
            new_user = User(
                username=stored_data['username'],
                first_name=stored_data['first_name'],
                last_name=stored_data['last_name'],
                phone=stored_data['phone'],
                user_type=stored_data['user_type'],
                password=stored_data['password'],  # Hash before saving in real case
                #email=stored_data['email']
            )

            # Add and commit the new user to the database
            db.session.add(new_user)
            db.session.commit()

            # Clear session data after successful registration
            session.pop('user_data', None)

            flash("Thanks for registering!")
            return redirect(url_for('main.login'))  # Redirect to login page after registration
        else:
            flash("Invalid OTP. Please try again.")
            return redirect(url_for('main.validate_otp'))

    return render_template('otp_validation_register.html')

@main.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = ''.join([
            request.form.get('otp1'),
            request.form.get('otp2'),
            request.form.get('otp3'),
            request.form.get('otp4'),
            request.form.get('otp5'),
            request.form.get('otp6')
        ])
        if entered_otp == str(session.get('otp')):
            print("yes")
            # OTP is correct, create a new user
            user_data = session['register_data']
            new_user = User(user_data['username'], user_data['first_name'], user_data['last_name'],
                            user_data['phone'], user_data['user_type'], user_data['password'])

            # Add and commit the new user to the database
            db.session.add(new_user)
            db.session.commit()

            # Clear the session data
            session.pop('otp', None)
            session.pop('register_data', None)

            return redirect(url_for('main.thank_you'))  # Use blueprint name

        else:
            flash("Invalid OTP! Please try again.")
            return redirect(url_for('main.verify_otp'))

    return render_template('otp_validation.html')  # Render OTP verification page
