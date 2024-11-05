# utils.py

import os
import yaml

def load_yaml_config(config_path="config.yaml"):
    """Carga la configuración YAML desde el archivo especificado."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def load_processed_files(log_file_path):
    """Carga los nombres de archivos procesados desde el log de archivos."""
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log:
            return set(log.read().splitlines())
    return set()

def update_processed_files(log_file_path, processed_files):
    """Actualiza el log de archivos procesados agregando nuevas entradas."""
    with open(log_file_path, 'a', encoding='utf-8') as log:
        for file in processed_files:
            log.write(f"{file}\n")

def ensure_directory_exists(directory_path):
    """Crea un directorio si no existe."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)