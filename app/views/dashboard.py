import base64
import random
from datetime import datetime
from io import BytesIO

import qrcode
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user, logout_user
from flask_mail import Message
from sqlalchemy import func

from app import db, mail
from app.models import ActivityLog
from .utils import send_email

dash_bp = Blueprint('dash', __name__)


@dash_bp.route('/account')
@login_required
def account():
    return redirect(url_for('dash.dashboard'))

@dash_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@dash_bp.route("/dashboard")
@login_required
def dashboard():
    days_since = (datetime.utcnow() - current_user.signup_date).days
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
        "dashboard.html",
        title="Eco Points Dashboard",
        username=email.split('@')[0],
        walking_data=walking_data,
        cycling_data=cycling_data,
        avg_data=avg_data,
        avg_cycling_data=avg_cycling_data,
        eco_points=int(total_eco_points),
        all_logs=[],
        days_since=days_since
    )



@dash_bp.route("/rewards", methods=["GET", "POST"])
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
                qr_data = f"{redeem_points} Eco Points = £{round(redeem_points * 0.02, 2)} | Code: {''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}"
                img = qrcode.make(qr_data)
                buffered = BytesIO()
                img.save(buffered)
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


@dash_bp.route("/send_qr_email", methods=["POST"])
@login_required
def send_qr_email():
    qr_data = request.form.get('qr_data', '')
    redeemed_points = request.form.get('redeemed_points', '0')

    if not qr_data:
        flash('QR data missing. Please redeem again.', 'danger')
        return redirect(url_for('dash.rewards'))

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered)
    buffered.seek(0)

    # Compose a styled HTML email
    subject = "🎁 Your Eco Points Voucher is Here!"
    body_text = f"Redeemed {redeemed_points} points. QR attached."
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

    # Use the generic email function
    send_email(
        subject=subject,
        recipients=[current_user.email],
        body=body_text,
        html=html_body,
        attachments=[("eco_voucher.png", "image/png", buffered.read())]
    )

    flash("QR voucher sent to your email 📩", "success")
    return redirect(url_for("dash.rewards"))