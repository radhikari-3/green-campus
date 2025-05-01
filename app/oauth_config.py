import json
import os, pickle, base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES     = ['https://www.googleapis.com/auth/gmail.send']
CREDS_FILE = os.path.join(os.getcwd(), 'credentials.json')
TOKEN_FILE = os.path.join(os.getcwd(), 'token.pickle')

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = json.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_console()
        with open(TOKEN_FILE, 'wb') as f:
            json.dump(creds, f)
    return build('gmail', 'v1', credentials=creds)

def send_email_via_gmail(to: str, subject: str, body: str):
    svc = get_gmail_service()
    mime = MIMEText(body)
    mime['to']      = to
    mime['from']    = 'me'
    mime['subject'] = subject
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    svc.users().messages().send(userId='me', body={'raw': raw}).execute()
