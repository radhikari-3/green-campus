from datetime import datetime, timedelta
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import Blueprint, render_template, redirect, flash, url_for, request, current_app
from flask_login import login_user, current_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.forms import (
    LoginForm, PasswordChangeForm, ResetOTPForm,
    ResetPasswordRequestForm, VerifyEmailForm,
    SignupForm, ResetPasswordForm
)
from app.models import User

# Blueprint setup
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ---------------------
# Utility Functions
# ---------------------
def generate_otp(user):
    import random
    otp = f"{random.randint(100000, 999999)}"
    user.email_otp = otp
    user.email_otp_expires = datetime.utcnow() + timedelta(minutes=10)
    return otp


def send_email(subject, recipients, body, html=None):
    """
    Helper function to send an email using Flask-Mail.

    Args:
        subject (str): The subject of the email.
        recipients (list): List of recipient email addresses.
        body (str): The plain text body of the email.
        html (str, optional): The HTML content of the email. If None, a simple HTML version is generated.

    Returns:
        None
    """
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html if html else f"<h3>{subject}</h3><p>{body}</p>",
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    from flask_mail import Mail
    mail = Mail(current_app)
    mail.send(msg)

# ---------------------
# Routes
# ---------------------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SignupForm()
    if form.validate_on_submit():
        if db.session.scalar(sa.select(User).where(User.email == form.email.data)):
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.signup'))

        user = User(email=form.email.data)
        user.set_password(form.password.data)
        otp = generate_otp(user)

        db.session.add(user)
        db.session.commit()

        send_email(
            subject="Verify Your Email",
            recipients=[user.email],
            body=f"Your OTP is {otp} (valid for 10 minutes).",
            html=f"<h3>Verify Your Email</h3><p>Your OTP is <strong>{otp}</strong> (valid for 10 minutes).</p>"
        )

        flash(f'OTP sent to your email {user.email}.', 'info')
        return redirect(url_for('auth.verify_email', user_id=user.id))

    return render_template('generic_form.html', title='Sign Up', form=form)


@auth_bp.route('/verify/<int:user_id>', methods=['GET', 'POST'])
def verify_email(user_id):
    user = db.session.get(User, user_id)
    form = VerifyEmailForm()

    if form.validate_on_submit():
        if user.email_otp == form.otp.data and user.email_otp_expires > datetime.utcnow():
            user.email_verified = True
            user.email_otp = None
            user.email_otp_expires = None
            db.session.commit()
            flash('Email verified! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        flash('Invalid or expired OTP.', 'danger')

    return render_template('generic_form.html', title='Verify Email', form=form)


@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user and user.email_verified:
            otp = generate_otp(user)
            db.session.commit()

            send_email(
                subject="Password reset OTP",
                recipients=[user.email],
                body=f"Your OTP is {otp} (valid for 10 minutes).",
                html=f"<h3>Password reset OTP</h3><p>Your OTP is <strong>{otp}</strong> (valid for 10 minutes).</p>"
            )

            flash('OTP sent to your email.', 'info')
            return redirect(url_for('auth.forgot_password_verify', user_id=user.id))

    return render_template('generic_form.html', title='Forgot Password', form=form)


@auth_bp.route('/forgot_password_verify/<int:user_id>', methods=['GET', 'POST'])
def forgot_password_verify(user_id):
    form = ResetOTPForm()
    user = db.session.get(User, user_id)

    if form.validate_on_submit():
        if user.email_otp == form.otp.data and user.email_otp_expires > datetime.utcnow():
            user.email_otp = None
            user.email_otp_expires = None
            db.session.commit()
            return redirect(url_for('auth.forgot_password_reset', user_id=user.id))
        flash('Invalid or expired OTP.', 'danger')

    return render_template('generic_form.html', title='Verify OTP', form=form)


@auth_bp.route('/forgot_password_reset/<int:user_id>', methods=['GET', 'POST'])
def forgot_password_reset(user_id):
    form = ResetPasswordForm()
    user = db.session.get(User, user_id)

    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been reset. You may now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('generic_form.html', title='New Password', form=form)


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    form = PasswordChangeForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password incorrect.', 'danger')
            return redirect(url_for('auth.reset_password'))

        current_user.set_password(form.new_password.data)
        current_user.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been changed.', 'success')
        return redirect(url_for('dash.account'))

    return render_template('generic_form.html', title='Change Password', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if 'Normal' not in current_user.role:  # Replace 'Normal' with the required role for the page
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        else:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))

        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('vendors.smart_food_expiry' if 'Vendor' in user.role else 'dash.dashboard')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)