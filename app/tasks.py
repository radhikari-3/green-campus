import logging
from smtplib import SMTPRecipientsRefused, SMTPException

from flask import current_app
from flask_mail import Message
from sqlalchemy import select

from app.extensions import db
from app.models import User
from app.utils import send_email
from app.views.food_expiry import get_updated_daily_discounts

# === Scheduled Task: Send Daily Discount Email ===
def scheduled_send_discount_email():
    """
    Main function executed by the APScheduler to:
    - Fetch expiring products
    - Generate discount offers
    - Send a formatted email with the deals to all users
    """
    with current_app.app_context():
        recipients = _get_recipient_emails()

        if not recipients:
            logging.info("No recipients found. Email not sent.")
            return

        # Step 1: Update discounts in DB for the next 3 days
        get_updated_daily_discounts(3)

        # Step 2: Fetch products expiring in the next 1 day
        products = get_updated_daily_discounts(1)

        if not products:
            logging.info("No expiring products to include in discount email.")
            return

        try:
            subject = "Items with major discounts, expiring in 1 day! 🌱"
            msg = _compose_discount_email(recipients, products, subject)

            # Use custom email function to send with optional formatting and attachment
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


# === Helper: Fetch All Verified Email Recipients ===
def _get_recipient_emails():
    """
    Retrieves a list of all user email addresses for email dispatch.
    """
    return [
        user.email.strip()
        for user in db.session.scalars(select(User)).all()
        if user.email
    ]


# === Helper: Create Formatted Email Message ===
def _compose_discount_email(recipients, products, subject):
    """
    Composes an email message with both HTML and plain text versions.
    """
    html_body = _generate_html_table(products, subject)
    text_body = _generate_plain_text(products)

    msg = Message(subject, bcc=recipients)
    msg.body = text_body
    msg.html = html_body
    return msg


# === Helper: Generate HTML Table Body for Discount Email ===
def _generate_html_table(products, subject):
    """
    Creates a styled HTML table showing product discount details.
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
        <p style="text-align: center;">🍇 Here are our products with exciting offers which expire soon:</p>
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


# === Helper: Generate Plain Text Body for Discount Email ===
def _generate_plain_text(products):
    """
    Creates a text-only fallback version of the discount email.
    """
    lines = ["Name | Expiry | Units | Marked Price | Final Price | Location", "-" * 60]
    for p in products:
        lines.append(f"{p.name} | {p.expiry_date:%Y-%m-%d} | {p.units} | £{p.marked_price:.2f} | £{p.final_price:.2f} | {p.location}")
    lines.append("\n© 2025 Green Campus Initiative. Empowering Sustainable Change.")
    return "\n".join(lines)
