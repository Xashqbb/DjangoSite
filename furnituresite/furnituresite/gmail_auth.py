import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None

    # Якщо вже є токен → використовуємо
    if os.path.exists('token.pkl'):
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)

    # Якщо токену нема або він прострочений
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            try:
                # Спочатку пробуємо локальний сервер
                creds = flow.run_local_server(port=8080)
            except Exception as e:
                print(f"⚠️ Проблема з локальним сервером: {e}")
                print("➡ Використовуємо консольний режим авторизації...")
                creds = flow.run_console()

        # Зберігаємо токен
        with open('token.pkl', 'wb') as token:
            pickle.dump(creds, token)

    return creds
