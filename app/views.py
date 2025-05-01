#views.py
from urllib.parse import urlsplit
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app.oauth_config import send_email_via_gmail
from datetime import datetime
import sqlalchemy as sa
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, VerifyEmailForm, SignupForm, ResetPasswordForm, ResetPasswordRequestForm, PasswordChangeForm, ResetOTPForm
from app.models import User
import sys

@app.route("/")
def home():
    return render_template('home.html', title="Home")

@app.route('/account')
@login_required
def account():
    days_since = (datetime.utcnow() - current_user.signup_date).days
    return render_template('account.html', title="Account", days_since_signup = days_since)


# helper to get serializer
def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- SIGNUP ---
@app.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        existing = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if existing:
            flash('Email already registered','danger')
            return redirect(url_for('signup'))
        u = User(email=form.email.data)
        u.set_password(form.password.data)
        otp = u.generate_otp()
        db.session.add(u); db.session.commit()

        send_email_via_gmail(
            to = u.email,
            subject = "Your Verification Code",
            body = f"Your signup code is {otp}. It expires in 10 minutes."
        )
        flash('OTP sent to your email.','info')
        return redirect(url_for('verify_email', user_id=u.id))
    return render_template('generic_form.html', title='Sign Up', form=form)


@app.route('/verify/<int:user_id>', methods=['GET','POST'])
def verify_email(user_id):
    u = db.session.get(User, user_id)
    form = VerifyEmailForm()
    if form.validate_on_submit():
        if u.email_otp == form.otp.data and u.email_otp_expires > datetime.utcnow():
            u.email_verified = True
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            flash('Email verified! You can now log in.','success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired OTP.','danger')
    return render_template('generic_form.html', title='Verify Email', form=form)


@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = ResetPasswordRequestForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if form.validate_on_submit():
        u = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)
        )
        if u and u.email_verified:
            otp = u.generate_otp()
            db.session.commit()
            send_email_via_gmail(
                to=u.email,
                subject="Password reset OTP",
                body=f"Your OTP is {otp} (valid 10 min)."
            )
            flash('OTP sent to your email.', 'info')
        return redirect(url_for('forgot_password_verify', user_id=u.id))
    return render_template('generic_form.html', title='Forgot Password', form=form)

@app.route('/forgot_password_verify/<int:user_id>', methods=['GET','POST'])
def forgot_password_verify(user_id):
    form = ResetOTPForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        if (u.email_otp == form.otp.data
            and u.email_otp_expires > datetime.utcnow()):
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            return redirect(url_for('forgot_password_reset', user_id=user_id))
        flash('Invalid or expired OTP.', 'danger')
    return render_template('generic_form.html', title='Verify OTP', form=form)

@app.route('/forgot_password_reset/<int:user_id>', methods=['GET','POST'])
def forgot_password_reset(user_id):
    form = ResetPasswordForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        u.set_password(form.password.data)
        u.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been reset. You may now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('generic_form.html', title='New Password', form=form)


@app.route('/reset_password', methods=['GET','POST'])
@login_required
def reset_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password incorrect.', 'danger')
            return redirect(url_for('reset_password'))
        current_user.set_password(form.new_password.data)
        current_user.signup_date = datetime.utcnow()
        db.session.commit()
        flash('Your password has been changed.', 'success')
        return redirect(url_for('account'))
    return render_template('generic_form.html', title='Change Password', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        if not user.email_verified:
            flash('Please verify your email before logging in.', 'warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500