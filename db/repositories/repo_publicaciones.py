import re
from typing import Dict, Optional
from db.mssql_connection import MSSQLConnector
from config import CONNECTION_DB, get_logger

logger = get_logger('db.repositories.publicaciones')

class PublicacionesRepository:
    def create(self, titulo: str, fecha: str, is_active: bool) -> Dict:
        query = """
            INSERT INTO publicaciones (titulo, fecha, is_active)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?);
        """
        params = (titulo, fecha, is_active)
        query_clean = re.sub(r'\s+', ' ', query).strip()

        with MSSQLConnector(**CONNECTION_DB) as conn:
            try:
                breakpoint() 
                result = conn.execute_query(query_clean, tuple(params))
                logger.debug(f"Resultado de INSERT: {result}")
                breakpoint()
                if result and len(result) > 0:
                    # El resultado es una lista de diccionarios
                    row = result[0]
                    # Puede venir como 'id' o como el nombre de la columna según el driver
                    new_id = row.get('id')
                    if new_id is None:
                        # Si no encuentra 'id', intenta con el primer valor (por índice)
                        new_id = list(row.values())[0] if row else None
                    if new_id is not None:
                        return {"id": int(new_id)}
                logger.error("No se pudo obtener el ID después de la inserción")
                return {}
            except Exception as e:
                breakpoint()
                logger.exception(f"Error al insertar publicacion: {e}")
                return {}

    def create_old(self, titulo: str, fecha: str, is_active: bool) -> Dict:
        insert_query = """
            INSERT INTO publicaciones (titulo, fecha, is_active)
            VALUES (?, ?, ?);
        """
        select_id_query = "SELECT SCOPE_IDENTITY() AS id;"
        
        conn_obj = MSSQLConnector(**CONNECTION_DB)
        conn_obj.connect()
        try:
            cursor = conn_obj.connection.cursor()
            cursor.execute(insert_query, (titulo, fecha, 1 if is_active else 0))
            # Insertar
            # Obtener el ID insertado
            cursor.execute(select_id_query)
            row = cursor.fetchone()
            print(row)
            new_id = row[0] if row else None
            conn_obj.connection.commit()
            if new_id is not None:
                return {"id": int(new_id)}
            else:
                logger.error("No se pudo obtener SCOPE_IDENTITY()")
                return {}
        except Exception as e:
            conn_obj.connection.rollback()
            logger.exception(f"Error en create: {e}")
            return {}
        finally:
            cursor.close()
            conn_obj.disconnect()

    def update(self, id: int, titulo: str, fecha: str, is_active: bool) -> bool:
        query = """
            UPDATE publicaciones
            SET titulo=?, fecha=?, is_active=?
            WHERE id=?
        """
        with MSSQLConnector(**CONNECTION_DB) as conn:
            conn.execute_query(query, (titulo, fecha, int(is_active), id))
            return True

    def delete(self, id: int) -> bool:
        query = "DELETE FROM publicaciones WHERE id=?"
        with MSSQLConnector(**CONNECTION_DB) as conn:
            conn.execute_query(query, (id,))
            return True

    def get_by_id(self, id: int) -> Optional[Dict]:
        query = "SELECT id, titulo, fecha, is_active FROM publicaciones WHERE id=?"
        with MSSQLConnector(**CONNECTION_DB) as conn:
            results = conn.execute_query(query, (id,))
            return results[0] if results else None