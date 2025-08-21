import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from gmail_auth import get_credentials

def send_gmail(to, subject, body):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_message = {
        'raw': raw_message
    }

    service.users().messages().send(userId="me", body=send_message).execute()
