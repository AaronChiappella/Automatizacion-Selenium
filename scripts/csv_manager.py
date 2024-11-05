# csv_manager.py

import csv
import os
import yaml
from datetime import datetime
from dotenv import load_dotenv


# Cargar variables de entorno
load_dotenv()

# Definir carpeta de reportes CSV
CSV_REPORTS_FOLDER = os.getenv("CSV_REPORTS_PATH")

# Cargar Configuración
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

# Definir carpeta de reportes CSV
config = load_config()
CSV_REPORTS_FOLDER = os.path.abspath(config["paths"]["csv_reports"])

# Función para guardar una línea en el archivo CSV general
def save_summary_line(csv_line):
    
    # Crear la carpeta csv_reports si no existe
    if not os.path.exists(CSV_REPORTS_FOLDER):
        os.makedirs(CSV_REPORTS_FOLDER)

    # Generar el nombre del archivo CSV del día
    current_date = datetime.now().strftime('%d-%m-%Y')
    file_name = f"resumen_{current_date}.csv"
    file_path = os.path.join(CSV_REPORTS_FOLDER, file_name)

    # Si el archivo no existe, crearlo con encabezados
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Número de Resolución", "Fecha", "Nombre", "Apellido", "DNI", "Categoría"])

    # Añadir la línea CSV al archivo existente
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_line.split(','))  # Separar la línea CSV en columnas