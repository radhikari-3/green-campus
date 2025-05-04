import io
import base64
import qrcode
from io import BytesIO
from datetime import datetime
from urllib.parse import urlsplit
from flask_mail import Message
from app import mail
import sqlalchemy as sa
from sqlalchemy import func
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import (
    LoginForm, VerifyEmailForm, SignupForm, ResetPasswordForm,
    ResetPasswordRequestForm, PasswordChangeForm, ResetOTPForm
)
from app.models import User, ActivityLog
from app.oauth_config import send_email_via_gmail


@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account")
@login_required
def account():
    days_since = (datetime.utcnow() - current_user.signup_date).days
    return render_template('account.html', title="Account", days_since_signup=days_since)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = SignupForm()
    if form.validate_on_submit():
        existing = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if existing:
            flash("Email already registered", "danger")
            return redirect(url_for("signup"))
        u = User(email=form.email.data)
        u.set_password(form.password.data)
        otp = u.generate_otp()
        db.session.add(u)
        db.session.commit()
        send_email_via_gmail(
            to=u.email,
            subject="Your Verification Code",
            body=f"Your signup code is {otp}. It expires in 10 minutes.",
        )
        flash("OTP sent to your email.", "info")
        return redirect(url_for("verify_email", user_id=u.id))
    return render_template("generic_form.html", title="Sign Up", form=form)


@app.route("/verify/<int:user_id>", methods=["GET", "POST"])
def verify_email(user_id):
    u = db.session.get(User, user_id)
    form = VerifyEmailForm()
    if form.validate_on_submit():
        if u.email_otp == form.otp.data and u.email_otp_expires > datetime.utcnow():
            u.email_verified = True
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            flash("Email verified! You can now log in.", "success")
            return redirect(url_for("login"))
        flash("Invalid or expired OTP.", "danger")
    return render_template("generic_form.html", title="Verify Email", form=form)


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        u = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if u and u.email_verified:
            otp = u.generate_otp()
            db.session.commit()
            send_email_via_gmail(
                to=u.email,
                subject="Password reset OTP",
                body=f"Your OTP is {otp} (valid 10 min).",
            )
            flash("OTP sent to your email.", "info")
            return redirect(url_for("forgot_password_verify", user_id=u.id))
    return render_template("generic_form.html", title="Forgot Password", form=form)


@app.route("/forgot_password_verify/<int:user_id>", methods=["GET", "POST"])
def forgot_password_verify(user_id):
    form = ResetOTPForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        if u.email_otp == form.otp.data and u.email_otp_expires > datetime.utcnow():
            u.email_otp = None
            u.email_otp_expires = None
            db.session.commit()
            return redirect(url_for("forgot_password_reset", user_id=user_id))
        flash("Invalid or expired OTP.", "danger")
    return render_template("generic_form.html", title="Verify OTP", form=form)


@app.route("/forgot_password_reset/<int:user_id>", methods=["GET", "POST"])
def forgot_password_reset(user_id):
    form = ResetPasswordForm()
    u = db.session.get(User, user_id)
    if form.validate_on_submit():
        u.set_password(form.password.data)
        u.signup_date = datetime.utcnow()
        db.session.commit()
        flash("Your password has been reset. You may now log in.", "success")
        return redirect(url_for("login"))
    return render_template("generic_form.html", title="New Password", form=form)


@app.route("/reset_password", methods=["GET", "POST"])
@login_required
def reset_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password incorrect.", "danger")
            return redirect(url_for("reset_password"))
        current_user.set_password(form.new_password.data)
        current_user.signup_date = datetime.utcnow()
        db.session.commit()
        flash("Your password has been changed.", "success")
        return redirect(url_for("account"))
    return render_template("generic_form.html", title="Change Password", form=form)


@app.route("/eco-points-dashboard")
@login_required
def eco_points_dashboard():
    email = current_user.email

    # Fetch walking activity
    walking_q = ActivityLog.query.filter_by(email=email, activity_type="walking").order_by(ActivityLog.date).all()
    walking_data = [
        {"date": al.date.strftime("%Y-%m-%d"), "steps": al.steps, "eco": round(al.eco_points, 2)}
        for al in walking_q
    ]

    # Fetch cycling activity
    cycling_q = ActivityLog.query.filter_by(email=email, activity_type="cycling").order_by(ActivityLog.date).all()
    cycling_data = [
        {"date": al.date.strftime("%Y-%m-%d"), "distance": al.distance, "eco": round(al.eco_points, 2)}
        for al in cycling_q
    ]

    # Average walking steps per day
    avg_q = (
        db.session.query(
            func.date(ActivityLog.date).label("date"),
            func.avg(ActivityLog.steps).label("avg_steps")
        )
        .filter(ActivityLog.activity_type == "walking")
        .group_by(func.date(ActivityLog.date))
        .order_by(func.date(ActivityLog.date))
        .all()
    )
    avg_data = [
        {"date": row.date.strftime("%Y-%m-%d"), "steps": round(row.avg_steps)}
        for row in avg_q
    ]

    # Average cycling distance per day
    avg_cycling_q = (
        db.session.query(
            func.date(ActivityLog.date).label("date"),
            func.avg(ActivityLog.distance).label("avg_distance")
        )
        .filter(ActivityLog.activity_type == "cycling")
        .group_by(func.date(ActivityLog.date))
        .order_by(func.date(ActivityLog.date))
        .all()
    )
    avg_cycling_data = [
        {"date": row.date.strftime("%Y-%m-%d"), "distance": round(row.avg_distance, 2)}
        for row in avg_cycling_q
    ]

    total_eco_points = db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0

    return render_template(
        "eco_points_dashboard.html",
        title="Eco Points Dashboard",
        username=email.split('@')[0],
        walking_data=walking_data,
        cycling_data=cycling_data,
        avg_data=avg_data,
        avg_cycling_data=avg_cycling_data,
        eco_points=int(total_eco_points),
        all_logs=[]
    )



@app.route("/rewards", methods=["GET", "POST"])
@login_required
def rewards():
    email = current_user.email
    total_points = db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0
    pounds = round(total_points * 0.02, 2)

    qr_url = None
    redeemed_points = None
    redeemed_value = None
    qr_data = ""

    if request.method == 'POST':
        try:
            redeem_points = int(request.form.get('redeem_points', 0))
            if 10 <= redeem_points <= total_points:
                qr_data = f"{redeem_points} Eco Points = £{round(redeem_points * 0.02, 2)}"
                img = qrcode.make(qr_data)
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                qr_url = f"data:image/png;base64,{img_str}"
                redeemed_points = redeem_points
                redeemed_value = round(redeem_points * 0.02, 2)

                # Update redeemed points in the database (already implemented)
                logs = ActivityLog.query.filter_by(email=email).order_by(ActivityLog.date).all()
                remaining = redeem_points
                for log in logs:
                    if remaining <= 0:
                        break
                    if log.eco_points > 0:
                        if log.eco_points <= remaining:
                            remaining -= log.eco_points
                            log.eco_points = 0
                        else:
                            log.eco_points -= remaining
                            remaining = 0
                db.session.commit()
            else:
                flash("You must redeem at least 10 points and not more than your balance.", "danger")
        except ValueError:
            flash("Invalid input. Please enter a number.", "danger")

    return render_template(
        "rewards.html",
        title="Redeem Eco Point Rewards",
        eco_points=int(
            db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0
        ),
        pounds=round(
            (db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0) * 0.02, 2
        ),
        qr_url=qr_url,
        qr_data=qr_data,
        redeemed_points=redeemed_points,
        redeemed_value=redeemed_value
    )


@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        body = request.form["body"]
        subject = request.form["subject"]
        msg = Message(subject=subject, recipients=[recipient])
        msg.body = body
        msg.html = "<h1>" + subject + "</h1>" + "<p>" + body + "</p>"
        mail.send(msg)
        flash(f'A test message was sent to {recipient}.')
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route("/send_qr_email", methods=["POST"])
@login_required
def send_qr_email():
    qr_data = request.form.get('qr_data', '')
    redeemed_points = request.form.get('redeemed_points', '0')

    if not qr_data:
        flash('QR data missing. Please redeem again.', 'danger')
        return redirect(url_for('rewards'))

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    # Compose a styled HTML email
    subject = "🎁 Your Eco Points Voucher is Here!"
    html_body = f"""
    <div style="font-family:Arial, sans-serif; padding: 20px; background-color:#f9f9f9;">
      <h2 style="color: #2e7d32;">🌿 Eco Points Voucher</h2>
      <p>Hello {current_user.email},</p>
      <p>Thank you for taking sustainable steps! 🎉</p>
      <p>You have successfully redeemed <strong>{redeemed_points} Eco Points</strong>.</p>
      <p>This equals <strong>£{round(int(redeemed_points) * 0.02, 2)}</strong> in rewards.</p>
      <p>Your voucher QR code is attached below.</p>

      <hr style="margin: 20px 0;">

      <p style="font-size: 0.9em; color: #666;">
        📌 Please present this voucher at participating partners to claim your reward. This is valid for one-time use only.
      </p>
    </div>
    """

    # Send email with attachment
    msg = Message(
        subject=subject,
        recipients=[current_user.email],
        body=f"Redeemed {redeemed_points} points. QR attached.",
        html=html_body
    )
    msg.attach("eco_voucher.png", "image/png", buffered.read())
    mail.send(msg)

    flash("QR voucher sent to your email 📩", "success")
    return redirect(url_for("rewards"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))
        if not user.email_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.errorhandler(403)
def error_403(error):
    return render_template("errors/403.html", title="Error"), 403


@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html", title="Error"), 404


@app.errorhandler(413)
def error_413(error):
    return render_template("errors/413.html", title="Error"), 413


@app.errorhandler(500)
def error_500(error):
    return render_template("errors/500.html", title="Error"), 500
