from config import DB_DRIVER
import pyodbc

from config import get_logger
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

logger = get_logger('db.mssql_connection')
import snoop

class MSSQLConnector:
    """
    Clase para conectarse a una base de datos MSSQL y realizar consultas.
    """

    def __init__(self, server: str, database: str, username: str, password: str):
        """
        Inicializa el conector con los parámetros de conexión.

        Args:
            server (str): Nombre o IP del servidor SQL Server
            database (str): Nombre de la base de datos
            username (str): Nombre de usuario
            password (str): Contraseña
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        self.driver = "ODBC Driver 17 for SQL Server" if not DB_DRIVER else DB_DRIVER
        logger.debug(f"Inicializado MSSQLConnector para servidor: {self.server}, base de datos: {self.database}")

    def connect(self) -> bool:
        """
        Establece la conexión con la base de datos.

        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            connection_string = (
                "DRIVER={" + self.driver + "};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;"
            )
            logger.debug(f"Intentando conexión con string: {connection_string.replace(self.password, '***')}")
            self.connection = pyodbc.connect(connection_string)
            logger.debug(f"Conexión exitosa a {self.server}/{self.database}")
            return True
        except pyodbc.Error as e:
            logger.critical(f"Error al conectar a la base de datos {self.server}/{self.database}: {e}")
            return False

    def disconnect(self):
        """
        Cierra la conexión con la base de datos si está abierta.
        """
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.debug(f"Conexión cerrada para {self.server}/{self.database}")
            except Exception as e:
                logger.error(f"Error al cerrar conexión: {e}")

    def execute_query_old(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Ejecuta una consulta SQL y devuelve los resultados.

        Args:
            query (str): Consulta SQL a ejecutar
            params (Optional[tuple]): Parámetros para la consulta parametrizada

        Returns:
            List[Dict]: Lista de diccionarios con los resultados
        """
        if not self.connection:
            if not self.connect():
                logger.warning("No se pudo establecer conexión para ejecutar query")
                return []

        try:
            cursor = self.connection.cursor()
            if params:
                # logger.debug(f"Ejecutando query parametrizada: {query} con params: {params}")
                cursor.execute(query, params)
            else:
                # logger.debug(f"Ejecutando query: {query}")
                cursor.execute(query)
    
            # Obtener nombres de columnas
            columns = [column[0] for column in cursor.description]

            # Convertir resultados a lista de diccionarios
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            logger.debug(f"Query ejecutada exitosamente. Resultados: {len(results)} registros")
            return results

        except pyodbc.Error as e:
            logger.error(f"Error al ejecutar la consulta: {query}. Error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al ejecutar query: {e}")
            return []
        finally:
            cursor.close()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        if not self.connection:
            if not self.connect():
                logger.warning("No se pudo establecer conexión para ejecutar query")
                return []

        cursor = self.connection.cursor()
        try:
            # 1. Sanitizar parámetros datetime para evitar conflictos con unixODBC
            if params:
                safe_params = tuple(
                    p.strftime("%Y-%m-%d %H:%M:%S") if isinstance(p, datetime) else p
                    for p in params
                )
                cursor.execute(query, safe_params)
            else:
                cursor.execute(query)

            # 2. LEER RESULTADOS PRIMERO (antes de commit)
            results = []
            if cursor.description is not None:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # 3. CONFIRMAR TRANSACCIÓN DESPUÉS de leer
            self.connection.commit()

            logger.debug(f"Query ejecutada exitosamente. Resultados: {len(results)} registros")
            return results if results else [{"rows_affected": cursor.rowcount}]

        except pyodbc.Error as e:
            self.connection.rollback()
            logger.error(f"Error de SQL al ejecutar consulta. Query: {query}. Error: {e}")
            raise e
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error inesperado al ejecutar query: {e}")
            raise e
        finally:
            cursor.close()
            
    def __enter__(self):
        """Permite usar la clase con el protocolo 'with'"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión al salir del bloque 'with'"""
        self.disconnect()
