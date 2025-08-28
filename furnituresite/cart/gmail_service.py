import sys
import os
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

# додаємо корінь проєкту в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from furnituresite.gmail_auth import get_credentials


def send_gmail(to, subject, body):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body, "html")
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print("✅ Email успішно відправлено:", to)
    except Exception as e:
        print("❌ Помилка при відправленні:", e)
