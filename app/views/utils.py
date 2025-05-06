from flask_mail import Message, Mail
from flask import current_app

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