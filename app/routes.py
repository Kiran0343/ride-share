from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from . import db

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
        phone_number = request.form['phone_number']
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

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Implement login functionality
    return render_template('login.html')

@main.route('/forgot-password')
def forgot_password():
    return render_template('login.html')
