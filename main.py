import os
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

# Anmeldedaten für den Zugriff auf die Gmail API
CLIENT_SECRET_FILE = '/Users/ichich/PycharmProjects/pythonProject22/client_secret.json'  # Pfad zur Client Secret JSON-Datei
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Erstellt eine Gmail API-Clientinstanz"""
    credentials = None

    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            credentials = flow.run_local_server(port=8000)

        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    service = build(API_NAME, API_VERSION, credentials=credentials)

    return service

def get_emails(service):
    """Ruft die 3 neuesten E-Mails ab"""
    try:
        result = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = result.get('messages')

        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            text = get_text(message)
            save_to_file(text)

    except HttpError as error:
        print(f'An error occurred: {error}')
        messages = []

    return messages

def get_text(message):
    """Extrahiert den Text aus einer E-Mail"""
    text = ''

    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                text += decoded_data

    else:
        if message['payload']['mimeType'] == 'text/plain':
            data = message['payload']['body']['data']
            decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
            text += decoded_data

    return text

def save_to_file(text):
    """Speichert den Text in einer Datei"""
    with open('emails.txt', 'a') as f:
        f.write(text)
        f.write('\n\n---\n\n')

if __name__ == '__main__':
    service = get_gmail_service()
    messages = get_emails(service)