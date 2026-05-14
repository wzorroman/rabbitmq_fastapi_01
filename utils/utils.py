import os
from datetime import datetime, timedelta
import re


def string_a_bool(valor):
    """Convierte diferentes representaciones de strings a valores booleanos."""
    if isinstance(valor, bool):
        return valor

    if not valor:
        raise ValueError("Se necesita un valor valido")

    if isinstance(valor, (int, float)):
        return bool(valor)

    if isinstance(valor, str):
        valor = valor.strip().lower()
        if valor in ('true', '1', 't', 'y', 'yes', 'sí', 'si'):
            return True
        elif valor in ('false', '0', 'f', 'n', 'no'):
            return False

    raise ValueError(f"No se puede convertir '{valor}' a booleano")

def clean_value(value):
    if value is None:
        return ''
    str_value = str(value).strip()
    return '' if str_value in ['', 'None', 'null'] else str_value

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def extract_date_from_filename(file_name: str, id_signal: str) -> str:
    """
    Extrae la fecha del nombre del archivo basado en el formato: {id}%Y%m%d_%H%M%S.{ext}

    Args:
        file_name: Nombre del archivo (ej: "9998720250826_194810.wmv")
        id_signal: ID de la señal (ej: "99987")

    Returns:
        str: Fecha en formato "YYYY-MM-DD HH:MM:SS" (ej: "2025-08-26 19:48:10")

    Raises:
        ValueError: Si el formato no coincide o la fecha es inválida
    """
    try:
        # Remover el ID y la extensión
        base_name = file_name.replace(id_signal, '').split('.')[0]

        # Parsear usando el formato esperado
        file_date = datetime.strptime(base_name, "%Y%m%d_%H%M%S")
        return file_date.strftime("%Y-%m-%d %H:%M:%S")

    except ValueError as e:
        raise ValueError(f"No se pudo parsear la fecha de {file_name}: {str(e)}")

def format_elapsed_time(time_delta) -> str:
    """
    Convierte segundos a formato legible: HH:MM:SS hrs, MM:SS min, o SS seg

    Args:
        seconds: Tiempo en segundos

    Returns:
        str: Tiempo formateado según la duración
    """
    # Si es un timedelta, obtener los segundos totales
    if hasattr(time_delta, 'total_seconds'):
        total_seconds = int(time_delta.total_seconds())
    else:
        # Si ya son segundos
        total_seconds = int(time_delta)

    if total_seconds >= 3600:  # Más de 1 hora
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds_remaining = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds_remaining:02d} hrs"
    elif total_seconds >= 60:  # Más de 1 minuto pero menos de 1 hora
        minutes = total_seconds // 60
        seconds_remaining = total_seconds % 60
        return f"{minutes:02d}:{seconds_remaining:02d} min"
    else:  # Menos de 1 minuto
        return f"{total_seconds:02d} seg"

def add_seconds_to_current_time(seconds: int, time_format: str = '%H:%M:%S') -> str:
    """
    Agrega segundos a la fecha/hora actual y devuelve el string formateado.

    Args:
        seconds (int): Segundos a agregar
        time_format (str): Formato de salida. Opciones:
            - '%H:%M:%S' (default) -> '15:30:45'
            - '%H:%M'              -> '15:30'
            - '%I:%M:%S %p'        -> '03:30:45 PM'
            - '%Y-%m-%d %H:%M:%S'  -> '2024-01-15 15:30:45'
            - 'full'               -> '2024-01-15 15:30:45'
            - 'time_only'          -> '15:30:45'
            - 'short_time'         -> '15:30'

    Returns:
        str: Hora futura formateada
    """
    # Mapeo de formatos predefinidos
    format_map = {
        'full': '%Y-%m-%d %H:%M:%S',
        'time_only': '%H:%M:%S',
        'short_time': '%H:%M',
        '12h': '%I:%M:%S %p'
    }

    # Usar formato mapeado o el proporcionado
    actual_format = format_map.get(time_format, time_format)

    current_time = datetime.now()
    future_time = current_time + timedelta(seconds=seconds)

    return future_time.strftime(actual_format)

def clean_transcript_text(text: str) -> str:
    """
    Limpia el texto de una transcripción:
    - Elimina saltos de línea (reemplaza por espacio)
    - Elimina espacios múltiples
    - Strip de espacios al inicio/final
    """
    if not isinstance(text, str):
        return ""
    # Reemplazar saltos de línea (\r\n, \n, \r) por espacio
    text = re.sub(r'[\r\n]+', ' ', text)
    # Reemplazar múltiples espacios por uno solo
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    return text.strip()


# Iconos para los estados
STATUS_ICONS = {
    'ACTIVO': '🟢',
    'INACTIVO': '🔴',
    'ERROR': '🟠',
    'default': '⚪'
}

