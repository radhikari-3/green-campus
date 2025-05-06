import logging
from smtplib import SMTPRecipientsRefused, SMTPException

from flask import current_app
from flask_mail import Message
from sqlalchemy import select

from app.extensions import db, mail
from app.models import User
from app.utils import send_email
from app.views.food_expiry import get_updated_daily_discounts


def scheduled_send_discount_email():
    with current_app.app_context():
        recipients = _get_recipient_emails()
        if not recipients:
            logging.info("No recipients found. Email not sent.")
            return

        # Apply and fetch updated discounts
        get_updated_daily_discounts(3)
        products = get_updated_daily_discounts(1)

        if not products:
            logging.info("No expiring products to include in discount email.")
            return

        try:
            subject = "Items with major discounts, expiring in 1 day! 🌱"
            msg = _compose_discount_email(recipients, products, subject)
            # Older function
            # mail.send(msg)
            # Use the generic email function
            send_email(
                subject=subject,
                bcc = [recipients],
                body=msg.body,
                html=msg.html,
            )


            logging.info(f"Discount email sent to {len(recipients)} recipients.")
        except SMTPRecipientsRefused as e:
            logging.error("Some recipients were refused: %s", e.recipients)
        except SMTPException as e:
            logging.error("SMTP error occurred: %s", str(e))


def _get_recipient_emails():
    return [
        user.email.strip()
        for user in db.session.scalars(select(User)).all()
        if user.email
    ]


def _compose_discount_email(recipients, products, subject):

    html_body = _generate_html_table(products, subject)
    text_body = _generate_plain_text(products)

    msg = Message(subject, bcc=recipients)
    msg.body = text_body
    msg.html = html_body
    return msg


def _generate_html_table(products, subject):
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

def _generate_plain_text(products):
    lines = ["Name | Expiry | Units | Marked Price | Final Price | Location", "-" * 60]
    for p in products:
        lines.append(f"{p.name} | {p.expiry_date:%Y-%m-%d} | {p.units} | £{p.marked_price:.2f} | £{p.final_price:.2f} | {p.location}")
    lines.append("\n© 2025 Green Campus Initiative. Empowering Sustainable Change.")
    return "\n".join(lines)