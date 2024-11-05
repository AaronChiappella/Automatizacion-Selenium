# main.py

import os
from datetime import datetime
import logging
from dotenv import load_dotenv  
from scripts.ai_interaction import get_summary_line
from scripts.csv_manager import save_summary_line
from scripts.email_notifier import send_email
from scripts.drive_handler import scan_and_download
from scripts.utils import (
    load_yaml_config,
    load_processed_files,
    update_processed_files,
    ensure_directory_exists
)

load_dotenv()

# Cargar la configuración
config = load_yaml_config()

# Definir rutas y configuraciones desde config
DOWNLOADS_FOLDER = os.path.abspath(config["paths"]["downloads"])
CSV_REPORTS_FOLDER = os.path.abspath(config["paths"]["csv_reports"])
LOG_FILE = os.path.abspath(config["paths"]["logs"])

# Asegurarse de que las carpetas existen
ensure_directory_exists(DOWNLOADS_FOLDER)
ensure_directory_exists(CSV_REPORTS_FOLDER)
ensure_directory_exists(LOG_FILE)

# Configuración de logging
log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')  # Ruta del archivo de log
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    handlers=[
                        logging.FileHandler(log_file_path, encoding='utf-8'),  # Guardar logs en archivo
                        logging.StreamHandler()  # Mostrar logs en consola
                    ])

# Función para procesar archivos descargados
def process_files():
    processed_files = load_processed_files(LOG_FILE)
    new_processed_files = set()

    for file_name in os.listdir(DOWNLOADS_FOLDER):
        file_path = os.path.join(DOWNLOADS_FOLDER, file_name)
        
        if file_name not in processed_files and file_path.endswith('.pdf'):
            try:
                csv_line = get_summary_line(file_path)  # Genera la línea de CSV
                save_summary_line(csv_line)  # Guarda la línea en el archivo CSV
                new_processed_files.add(file_name)
                logging.info(f"Archivo procesado: {file_name}")
            except Exception as e:
                logging.error(f"Error al procesar {file_name}: {e}")

    update_processed_files(LOG_FILE, new_processed_files)
    logging.info("Proceso completado. Los archivos nuevos fueron procesados y registrados.")

# Proceso principal de automatización
if __name__ == "__main__":
    try:
        scan_and_download()  # Descargar archivos nuevos desde Drive
    except Exception as e:
        logging.error(f"Error al descargar archivos desde Google Drive: {e}")

    process_files()

    # Definir el nombre y la ruta del archivo CSV de reporte
    current_date = datetime.now().strftime('%d-%m-%Y')
    csv_file_name = f"resumen_{current_date}.csv"
    csv_file_path = os.path.join(CSV_REPORTS_FOLDER, csv_file_name)

    if os.path.exists(csv_file_path):
        logging.info(f"Archivo CSV encontrado: {csv_file_path}")
        send_email(csv_file_path)
    else:
        logging.warning(f"No se encontró un archivo CSV en: {csv_file_path}")