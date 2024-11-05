# ai_interaction.py

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pynput.keyboard import Key, Controller
import time
import yaml
from dotenv import load_dotenv



# Cargar variables de entorno
load_dotenv()

IA_EMAIL = os.getenv("IA_EMAIL")
IA_PASSWORD = os.getenv("IA_PASSWORD")


# Cargar configuración y credenciales
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def get_summary_line(file_path):
    config = load_config()
    email, password = config["credentials"]["email"], config["credentials"]["password"]

    file_path = os.path.abspath(file_path)
    
    # Configuración de Selenium para abrir Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized") 
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--enable-javascript")
    driver = webdriver.Chrome(options=options)
    
    # Ingresar a poe.com
    driver.get('https://poe.com/login') 
    
    # Esperar hasta que el "inciar sesión" esté y se vea
    login_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/main/div[2]/div/button[1]'))
    )
    time.sleep(2)  # Esperar 2 segundos para asegurar que carga
    login_button.click() # Clickea

    # Esperar "Correo Electrónico"
    email_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "identifier"))
    )
    time.sleep(2)
    email_input.send_keys("trabajofinalautomatizacion@gmail.com")

    # Esperar "Siguiente"
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="identifierNext"]/div/button'))
    )
    time.sleep(2)
    next_button.click()

    # Esperar "Contraseña"
    password_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "Passwd"))
    )
    time.sleep(2)
    password_input.send_keys("automatizacion2024")

    # Esperar "Siguiente"
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="passwordNext"]/div/button'))
    )
    time.sleep(2)
    next_button.click()

    # Esperar Verificación
    next_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[3]/div/div/div[2]/div/div/button'))
    )
    time.sleep(2)
    next_button.click()

    # Esperar "Adjuntar Archivo"
    attach_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div[1]/div/main/div/div/div/div[1]/div/div[3]/div/div[2]/button'))
    )
    time.sleep(2)
    attach_button.click()
    
    # Ingresar ruta del archivo con el teclado y presionar Enter
    time.sleep(2)
    keyboard = Controller()
    keyboard.type(file_path) 
    time.sleep(1)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    # Cargar Solicitud
    summary_request = f"Hola, necesito extraer una línea en formato CSV de este archivo. Por favor, toma el número de resolución y la fecha del documento, y luego, de la sección nombrada 'ARTÍCULO 1°', extrae específicamente el nombre completo y el DNI de la persona designada (IGNORA OTROS NOMBRES QUE ESTÉN FUERA DE ARTÍCULO 1°). Asegúrate de que el nombre esté en el formato de nombre(s) seguido del apellido (por ejemplo: 'Joaquín René SUÁREZ'). La información debe estar en el siguiente orden y formato: número de resolución, fecha (DD/MM/AAAA), nombre(s), apellido (ambos extraídos del ARTÍCULO 1°), DNI (extraído del ARTÍCULO 1°), y categoría (solo el número, sin la palabra 'Categoría'). Responde solo con una línea en texto CSV, sin formato de código."
    chat_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'GrowingTextArea_textArea__ZWQbP'))
    )
    time.sleep(2)
    chat_input.send_keys(summary_request)    

    # Enviar Mensaje
    send_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.Button_primary__6UIn0.ChatMessageSendButton_sendButton__4ZyI4"))
    )
    time.sleep(2)
    send_button.click()
    
    # Capturar el resultado
    time.sleep(6)
    summary_line = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Message_leftSideMessageBubble__VPdk6"))
    ).text
    time.sleep(2)
    driver.quit()
    
    return summary_line # Devuelve línea CSV
