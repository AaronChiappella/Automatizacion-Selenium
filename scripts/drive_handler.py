import os
import pickle
import io
import yaml
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv


# Cargar variables de entorno
load_dotenv()

# Variables de configuración de Google Drive
DRIVE_CREDENTIALS_PATH = os.getenv("DRIVE_CREDENTIALS_PATH")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
DOWNLOADS_PATH = os.getenv("DOWNLOADS_PATH")


# Cargar credenciales de Google Drive
def load_drive_credentials():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["paths"]["credentials"]["drive"]

# Cargar configuración de Google Drive
def load_drive_config():
   with open("config.yaml", "r") as file:
       config = yaml.safe_load(file)
   return config["google_drive"]["folder_id"], config["paths"]["downloads"]

# Autenticación para Google Drive API
def authenticate_gdrive():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    drive_credentials_path = load_drive_credentials() 
    token_path = os.path.join(os.path.dirname(drive_credentials_path), 'token_drive.pickle')
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(drive_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('drive', 'v3', credentials=creds)

# Descargar el archivo desde Google Drive
def download_file(service, file_id, file_name, download_folder):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(download_folder, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
    print(f"File {file_name} downloaded successfully.")

# Obtener lista de archivos en una carpeta de Google Drive
def get_files_in_folder(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name)").execute()
    items = results.get('files', [])
    return items

# Escanear y descargar archivos desde Google Drive
def scan_and_download():
    folder_id, download_folder = load_drive_config()
    service = authenticate_gdrive()
    
    files = get_files_in_folder(service, folder_id)
    for file in files:
        file_name = file['name']
        file_path = os.path.join(download_folder, file_name)
        
        if not os.path.exists(file_path):  # Solo descargar si el archivo no existe localmente
            print(f"New file detected: {file_name}")
            download_file(service, file['id'], file_name, download_folder)