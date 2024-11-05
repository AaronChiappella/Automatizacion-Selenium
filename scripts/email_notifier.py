# email_notifier.py

import os
import pickle
import base64
import mimetypes
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import yaml
from dotenv import load_dotenv




# Cargar variables de entorno
load_dotenv()

# Variables de configuración
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENTS = os.getenv("RECIPIENTS").split(",")

# Cargar credenciales de Gmail
GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH")
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


# Cargar configuración de correo electrónico
def load_email_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["email_settings"]

email_config = load_email_config()
sender = email_config["sender_email"]
recipients = email_config["recipients"]

# Cargar credenciales de Gmail
def load_email_credentials():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["paths"]["credentials"]["gmail"]

# Define el alcance de acceso
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Función para crear un mensaje con un archivo opcional
def create_message(sender, to, subject, message_text, file_path=None):
    message = EmailMessage()
    message.set_content(message_text)
    message['To'] = to
    message['From'] = sender
    message['Subject'] = subject

    # Si se proporciona una ruta de archivo, agregarlo como adjunto
    if file_path:
        attachment_filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type, mime_subtype = mime_type.split('/')

        with open(file_path, 'rb') as file:
            message.add_attachment(file.read(),
                                   maintype=mime_type,
                                   subtype=mime_subtype,
                                   filename=attachment_filename)

    # Codificar el mensaje en base64
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': encoded_message}

# Función de enviar mensaje Gmail
def send_message(service, user_id, message):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Correo enviado con Message Id: {sent_message['id']}")
        return sent_message
    except Exception as error:
        print(f"Ocurrió un error: {error}")
        return None

# Función que envía mail
def send_email(file_path):
    creds = None
    email_credentials_path = load_email_credentials()
    token_path = os.path.join(os.path.dirname(email_credentials_path), 'token_email.pickle')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(email_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    # Conectarse a la API de Gmail
    service = build('gmail', 'v1', credentials=creds)

    # Generar fecha y hora actuales en Argentina
    argentina_time = datetime.utcnow() - timedelta(hours=3)
    current_date = argentina_time.strftime("%d-%m-%Y")
    current_hour = argentina_time.hour

    # Asunto
    custom_subject = f"Reporte de archivos del {current_date}"
    
    # Saludar según la hora
    saludo = "Buen día" if 6 <= current_hour < 18 else "Buenas noches"

    # Cuerpo del mensaje
    message_text = (
        f"{saludo},\n\n"
        f"Se adjunta el reporte diario de archivos procesados automáticamente. "
        f"Fecha de envío: {current_date}\n\n"
        f"Saludos Cordiales,\nEquipo de automatización"
    )

    # Crea y envía el mensaje
    message = create_message(sender, recipients, custom_subject, message_text, file_path)
    send_message(service, "me", message)