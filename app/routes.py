from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import User
from . import db
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate('ride-share.json')  # Replace with your actual path
firebase_admin.initialize_app(cred)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('app.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone']
        user_type = request.form['user_type']

        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type=user_type
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('main.home'))

    return render_template('register.html')

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
    # Implement login functionality
    return render_template('login.html')

@main.route('/forgot-password')
def forgot_password():
    return render_template('login.html')

