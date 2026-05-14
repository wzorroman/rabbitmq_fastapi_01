import os
import sys
import logging
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler

from utils.utils import string_a_bool

# Cargar variables del archivo .env
load_dotenv()

# Variables de configuración
VERSION_APP = "1.0.1"
try:
    ID_PC = int(os.getenv('ID_PC', 1))
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    BD_SERVER = os.getenv('BD_SERVER')
    BD_DATABASE = os.getenv('BD_DATABASE')
    BD_USER = os.getenv('BD_USER')
    BD_PASSWORD = os.getenv('BD_PASSWORD')
    
    # LuxorV2 (base de datos destino) – puede ser la misma u otra
    LUXORV2_SERVER = os.getenv('LUXORV2_SERVER')
    LUXORV2_DATABASE = os.getenv('LUXORV2_DATABASE')
    LUXORV2_USER = os.getenv('LUXORV2_USER')
    LUXORV2_PASSWORD = os.getenv('LUXORV2_PASSWORD')
   
except KeyError as key:
    print(f"\x1b[33m[ERROR] La clave {key} no existe\x1b[0m")
    sys.exit(1)

def setup_global_logging():
    """Configura el logging global para toda la aplicación"""
    try:
        # Crear directorio LOGS si no existe
        project_root = os.path.dirname(os.path.abspath(sys.argv[0]))
        log_dir = os.path.join(project_root, "LOGS")
        os.makedirs(log_dir, exist_ok=True)

        # Nombre del archivo de log diario
        #log_filename = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
        #daily_log_file = os.path.join(log_dir, log_filename)

        # Configurar el logger principal
        logger = logging.getLogger('app')
        logger.setLevel(logging.INFO)

        # Evitar que los mensajes se propaguen al logger root
        logger.propagate = False
        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter('%(asctime)s - [%(name)s:%(lineno)s] - %(levelname)s - %(message)s')

        log_filename = "app_daily.log"
        path_log_filename = os.path.join(log_dir, log_filename)

        # Handler para rotación diaria usando suffix
        daily_handler = TimedRotatingFileHandler(
            path_log_filename,
            when='midnight',      # Rotar a medianoche
            interval=1,           # Cada día
            backupCount=14,       # Conservar 14 días
            encoding='utf-8'
        )
        # Configurar el suffix para el formato YYYY-MM-DD
        daily_handler.suffix = "%Y-%m-%d"
        # Configurar el formato de los archivos rotados
        daily_handler.namer = lambda name: name.replace("app_daily.log", "multiencoder") + ".log"

        daily_handler.setFormatter(formatter)
        daily_handler.setLevel(logging.INFO)

        # Handler para consola (opcional)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Agregar handlers al logger
        logger.addHandler(daily_handler)
        # logger.addHandler(console_handler)  # Descomentar si quieres ver logs en consola

        # Logger principal de la aplicación
        logger.info(f"=== INICIO DE APLICACIÓN ({VERSION_APP}) === ID_PC: {ID_PC}")
        logger.info(f"Logging configurado en: {path_log_filename}")

        return logger, path_log_filename

    except Exception as e:
        print(f"Error crítico al configurar logging: {str(e)}")
        raise

# Inicializar logging global al importar el módulo
app_logger, LOG_FILE = setup_global_logging()

# Función para obtener logger en otros módulos
def get_logger(name):
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(f'app.{name}')

# OTRAS Variables
APP_PORT = int(os.getenv('APP_PORT', 8001))
APP_HOST = str(os.getenv('APP_HOST', "0.0.0.0"))
APP_TOKEN = str(os.getenv('APP_TOKEN', "AppT0k3nEnc1pt@doCu41qu13r@"))


CONNECTION_DB = {
    "server": BD_SERVER,
    "database": BD_DATABASE,
    "username": BD_USER,
    "password": BD_PASSWORD,
}

TEST_USE = string_a_bool(str(os.getenv('MODO_TEST_USE', False) ))
API_TOKEN = os.getenv('API_TOKEN', 'default-token-change-me-please')

CONNECTION_DB_TARGET = {
    "server": LUXORV2_SERVER,
    "database": LUXORV2_DATABASE,
    "username": LUXORV2_USER,
    "password": LUXORV2_PASSWORD,
}

# RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'luxor.cdc.publicaciones')
