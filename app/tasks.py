import logging
from smtplib import SMTPRecipientsRefused, SMTPException

from flask import current_app
from flask_mail import Message
from sqlalchemy import select

from app.extensions import db
from app.models import User
from app.utils import send_email
from app.views.food_expiry import get_updated_daily_discounts


# === Scheduled Task: Send Discount Email to Users ===

def scheduled_send_discount_email():
    """
    Runs as a scheduled job.
    Collects expiring product data and emails a discount table to all users.
    """
    with current_app.app_context():
        recipients = _get_recipient_emails()
        if not recipients:
            logging.info("No recipients found. Email not sent.")
            return

        # Apply discount logic to products expiring in 3 days and fetch those expiring in 1 day
        get_updated_daily_discounts(3)
        products = get_updated_daily_discounts(1)

        if not products:
            logging.info("No expiring products to include in discount email.")
            return

        try:
            subject = "Items with major discounts, expiring in 1 day!"
            msg = _compose_discount_email(recipients, products, subject)

            # Send the composed email using the abstracted SendGrid-based utility
            send_email(
                subject=subject,
                recipients=recipients,
                bcc=[recipients],
                body=msg.body,
                html=msg.html,
            )

            logging.info(f"Discount email sent to {len(recipients)} recipients.")

        except SMTPRecipientsRefused as e:
            logging.error("Some recipients were refused: %s", e.recipients)

        except SMTPException as e:
            logging.error("SMTP error occurred: %s", str(e))


# === Helper: Get All User Emails ===

def _get_recipient_emails():
    """
    Queries all user records and returns a clean list of their email addresses.
    """
    return [
        user.email.strip()
        for user in db.session.scalars(select(User)).all()
        if user.email
    ]


# === Helper: Compose Email Message ===

def _compose_discount_email(recipients, products, subject):
    """
    Generates a Flask-Mail `Message` object using both HTML and plain text bodies.
    """
    html_body = _generate_html_table(products, subject)
    text_body = _generate_plain_text(products)

    msg = Message(subject, bcc=recipients)
    msg.body = text_body
    msg.html = html_body
    return msg


# === Helper: Generate HTML Table for Email ===

def _generate_html_table(products, subject):
    """
    Generates an HTML email table with product discount details.
    """
    rows = "".join(f"""
        <tr>
            <td>{p.name}</td>
            <td>{p.expiry_date.strftime('%Y-%m-%d')}</td>
            <td>{p.units}</td>
            <td>£{p.marked_price:.2f}</td>
            <td>£{p.final_price:.2f}</td>
            <td>{p.location}</td>
        </tr>""" for p in products)

    return f"""
    <div style="background-color: #f4fcf7; padding: 20px;">
        <h2 style="text-align: center;">{subject}</h2>
        <p style="text-align: center;">Here are our products with exciting offers which expire soon:</p>
        <table border="1" cellspacing="0" cellpadding="4" style="margin: 0 auto;">
            <tr>
                <th>Product</th>
                <th>Expiry Date</th>
                <th>Units</th>
                <th>Marked Price</th>
                <th>Final Price</th>
                <th>Location</th>
            </tr>
            {rows}
        </table>
        <br><hr>
        <p style="font-size: 0.9em; color: gray; text-align: center;">
            © 2025 Green Campus Initiative. Empowering Sustainable Change.
        </p>
    </div>
    """


# === Helper: Generate Plain Text Version of Discount Email ===

def _generate_plain_text(products):
    """
    Builds a plain-text fallback for email clients that don't support HTML.
    """
    lines = ["Name | Expiry | Units | Marked Price | Final Price | Location", "-" * 60]
    for p in products:
        lines.append(f"{p.name} | {p.expiry_date:%Y-%m-%d} | {p.units} | £{p.marked_price:.2f} | £{p.final_price:.2f} | {p.location}")
    lines.append("\n© 2025 Green Campus Initiative. Empowering Sustainable Change.")
    return "\n".join(lines)
