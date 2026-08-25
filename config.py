# ============================================================
# IMPORTAR MÓDULO OS
# ============================================================

# 'os' permite interactuar con algunas funciones del sistema
# operativo.
#
# En este proyecto lo utilizamos principalmente para leer
# variables de entorno.
#
# En palabras sencillas:
# el sistema operativo puede guardar información como claves
# y configuraciones fuera del código, y Python puede leerlas.
import os


# ============================================================
# IMPORTAR DOTENV
# ============================================================

# 'load_dotenv' pertenece a la librería python-dotenv.
#
# Su función es leer el archivo .env del proyecto y cargar
# las variables que allí se encuentran.
#
# Por ejemplo, si nuestro .env tiene:
#
# BOT_TOKEN=123456
#
# después de ejecutar load_dotenv(), Python podrá obtener
# ese valor utilizando os.getenv("BOT_TOKEN").
#
# Esto es útil porque no necesitamos escribir directamente
# las claves y contraseñas dentro del código.
from dotenv import load_dotenv


# ============================================================
# CARGAR VARIABLES DEL ARCHIVO .ENV
# ============================================================

# Esta función busca el archivo .env y carga sus variables
# de entorno para que puedan ser utilizadas por el programa.
#
# En palabras sencillas:
# es como decirle a Python:
#
# "Ve a buscar las configuraciones secretas que guardé
# en el archivo .env y déjalas disponibles".
load_dotenv()


# ============================================================
# TOKEN DEL BOT DE TELEGRAM
# ============================================================

# os.getenv("BOT_TOKEN") busca una variable llamada
# BOT_TOKEN dentro de las variables de entorno.
#
# El valor corresponde al token que Telegram proporciona
# para identificar y controlar nuestro bot.
#
# IMPORTANTE:
# El token no está escrito directamente en el código.
# Se encuentra en el archivo .env.
#
# Esto es más seguro y además facilita posteriormente
# subir el proyecto a la nube sin tener que modificar
# el código fuente.
BOT_TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# CLAVE DE LA API DE GEMINI
# ============================================================

# Aquí obtenemos la clave de acceso a la API de Gemini.
#
# Esta clave permite que nuestro programa pueda comunicarse
# con los modelos de inteligencia artificial de Google.
#
# Al igual que el token de Telegram, la clave se guarda
# en .env y no directamente en el código.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# MODELO DE GEMINI
# ============================================================

# Aquí obtenemos de las variables de entorno el nombre
# del modelo de Gemini que queremos utilizar.
#
# En nuestro .env tenemos una variable llamada GEMINI_MODEL.
#
# Por ejemplo:
#
# GEMINI_MODEL=gemini-2.5-flash-lite
#
# De esta manera podemos cambiar el modelo desde el archivo
# .env sin tener que modificar ai_service.py.
#
# En palabras sencillas:
# este valor le dice al programa:
#
# "Cuando necesites hablar con la inteligencia artificial,
# utiliza este modelo".
#
# El segundo argumento:
#
# "models/gemini-flash-latest"
#
# funciona como valor predeterminado.
#
# Es decir, si GEMINI_MODEL no existe en .env, Python
# utilizará ese valor.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "models/gemini-flash-latest"
)


# ============================================================
# URL DE GOOGLE APPS SCRIPT
# ============================================================

# Aquí obtenemos la URL de nuestra aplicación web de
# Google Apps Script.
#
# Esta URL es la dirección a la que Python envía las
# solicitudes relacionadas con Google Calendar.
#
# Por ejemplo:
#
# Python
#   ↓
# calendar_service.py
#   ↓
# Google Apps Script
#   ↓
# Google Calendar
#
# La URL se guarda en .env para no escribirla directamente
# dentro del código.
#
# En palabras sencillas:
# es como la "dirección postal" de nuestro Apps Script.
# Cuando nuestro bot necesita crear o consultar un evento,
# sabe a qué dirección enviar la información.
URL_APPS_SCRIPT = os.getenv("URL_APPS_SCRIPT")