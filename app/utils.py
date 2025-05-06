import json
import os

from flask import current_app
from flask_mail import Message, Mail

from app import logger

basedir = os.path.abspath(os.path.dirname(__file__))

def send_email(subject: str,recipients: list,body: str = '',html: str = None,
    cc: list = None,bcc: list = None,attachments: list = None,sender: str = None) -> None:
    msg = Message(
        subject=subject,
        recipients=recipients,
        cc=cc,
        bcc=bcc,
        body=body,
        html=html if html else f"<h3>{subject}</h3><p>{body}</p>",
        sender=sender or current_app.config.get('MAIL_DEFAULT_SENDER')
    )

    if attachments:
        for filename, content_type, data in attachments:
            msg.attach(filename, content_type, data)

    mail = Mail(current_app)
    mail.send(msg)

def load_buildings_data():
    file_path = os.path.join(basedir, 'static', 'buildings_data.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            university_buildings = data.get('university_buildings', [])
            accommodation_buildings = data.get('accommodation_buildings', [])
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        university_buildings = []
        accommodation_buildings = []
    return university_buildings, accommodation_buildings