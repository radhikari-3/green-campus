import base64
import random
from datetime import datetime
from io import BytesIO

import qrcode
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func

from app import db
from app.models import ActivityLog
from app.utils import send_email

# === Blueprint Setup ===
dash_bp = Blueprint('dash', __name__)


# === Route: Redirect to Dashboard if Logged In ===
@dash_bp.route('/account')
@login_required
def account():
    return redirect(url_for('dash.dashboard'))


# === Route: Logout User and Redirect to Home ===
@dash_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# === Route: Main Dashboard ===
@dash_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Displays user's dashboard with activity statistics and eco point balance.
    """
    email = current_user.email
    days_since = (datetime.utcnow() - current_user.signup_date).days

    walking_data = fetch_activity_data(email, "walking")
    cycling_data = fetch_activity_data(email, "cycling")
    avg_data = fetch_average_data("walking", "steps")
    avg_cycling_data = fetch_average_data("cycling", "distance")
    total_eco_points = calculate_total_eco_points(email)

    return render_template(
        "user_dashboard.html",
        title="Eco Points Dashboard",
        username=email.split('@')[0],
        walking_data=walking_data,
        cycling_data=cycling_data,
        avg_data=avg_data,
        avg_cycling_data=avg_cycling_data,
        eco_points=int(total_eco_points),
        all_logs=[],
        electricity_units=int(total_eco_points) * 0.37,  # Conversion example
        days_since=days_since
    )


# === Route: Redeem Eco Points and Generate QR Voucher ===
@dash_bp.route("/rewards", methods=["GET", "POST"])
@login_required
def rewards():
    """
    Allows users to redeem eco points for rewards and receive a QR code.
    """
    email = current_user.email
    total_points = calculate_total_eco_points(email)
    pounds = round(total_points * 0.02, 2)

    qr_url = None
    redeemed_points = None
    redeemed_value = None
    qr_data = ""

    if request.method == 'POST':
        try:
            redeem_points = int(request.form.get('redeem_points', 0))
            if 10 <= redeem_points <= total_points:
                # Create QR code content
                qr_data = f"{redeem_points} Eco Points = £{round(redeem_points * 0.02, 2)} | Code: {''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}"
                qr_url = generate_qr_code(qr_data)
                redeemed_points = redeem_points
                redeemed_value = round(redeem_points * 0.02, 2)

                # Update eco point balance
                update_redeemed_points(email, redeem_points)
            else:
                flash("You must redeem at least 10 points and not more than your balance.", "danger")
        except ValueError:
            flash("Invalid input. Please enter a number.", "danger")

    return render_template(
        "rewards.html",
        title="Redeem Eco Point Rewards",
        eco_points=total_points,
        pounds=pounds,
        qr_url=qr_url,
        qr_data=qr_data,
        redeemed_points=redeemed_points,
        redeemed_value=redeemed_value
    )


# === Route: Send QR Voucher to User's Email ===
@dash_bp.route("/send_qr_email", methods=["POST"])
@login_required
def send_qr_email():
    """
    Sends the QR code to the user's email as a PNG attachment.
    """
    qr_data = request.form.get('qr_data', '')
    redeemed_points = request.form.get('redeemed_points', '0')

    if not qr_data:
        flash('QR data missing. Please redeem again.', 'danger')
        return redirect(url_for('dash.rewards'))

    qr_url = generate_qr_code(qr_data)
    email_payload = create_email_payload(current_user.email, redeemed_points)

    send_email(
        subject=email_payload["subject"],
        recipients=[current_user.email],
        body=email_payload["body_text"],
        html=email_payload["html_body"],
        attachments=[("eco_voucher.png", "image/png", BytesIO(base64.b64decode(qr_url.split(",")[1])).read())]
    )

    flash("QR voucher sent to your email 📩", "success")
    return redirect(url_for("dash.rewards"))


# === Helper: Compose Email Content for QR Code ===
def create_email_payload(user_email, redeemed_points):
    subject = "🎁 Your Eco Points Voucher is Here!"
    body_text = f"Redeemed {redeemed_points} points. QR attached."
    html_body = f"""
    <div style="font-family:Arial, sans-serif; padding: 20px; background-color:#f9f9f9;">
      <h2 style="color: #2e7d32;">🌿 Eco Points Voucher</h2>
      <p>Hello {user_email},</p>
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
    return {"subject": subject, "body_text": body_text, "html_body": html_body}


# === Helper: Fetch Time-Series Activity Log Data ===
def fetch_activity_data(email, activity_type):
    query = ActivityLog.query.filter_by(email=email, activity_type=activity_type).order_by(ActivityLog.date).all()
    if activity_type == "walking":
        return [{"date": al.date.strftime("%Y-%m-%d"), "steps": al.steps, "eco": round(al.eco_points, 2)} for al in query]
    elif activity_type == "cycling":
        return [{"date": al.date.strftime("%Y-%m-%d"), "distance": al.distance, "eco": round(al.eco_points, 2)} for al in query]
    return []


# === Helper: Fetch Average Metrics Across Users per Day ===
def fetch_average_data(activity_type, metric):
    avg_query = (
        db.session.query(
            func.date(ActivityLog.date).label("date"),
            func.avg(getattr(ActivityLog, metric)).label(f"avg_{metric}")
        )
        .filter(ActivityLog.activity_type == activity_type)
        .group_by(func.date(ActivityLog.date))
        .order_by(func.date(ActivityLog.date))
        .all()
    )
    return [{"date": row.date.strftime("%Y-%m-%d"), metric: round(getattr(row, f"avg_{metric}"), 2)} for row in avg_query]


# === Helper: Calculate Total Eco Points for Current User ===
def calculate_total_eco_points(email):
    return db.session.query(func.sum(ActivityLog.eco_points)).filter(ActivityLog.email == email).scalar() or 0


# === Helper: Subtract Redeemed Points from Activity Logs ===
def update_redeemed_points(email, redeem_points):
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


# === Helper: Generate QR Code and Return Base64 URL ===
def generate_qr_code(data):
    img = qrcode.make(data)
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
