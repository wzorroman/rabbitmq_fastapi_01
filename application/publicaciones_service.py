# file: application/publicaciones_service.py
import uuid
from db.repositories.repo_publicaciones import PublicacionesRepository
from cdc.producer import publish_change
from config import get_logger

logger = get_logger('application.publicaciones_service')

class PublicacionesService:
    def __init__(self):
        self.repo = PublicacionesRepository()

    def crear(self, titulo: str, fecha: str, is_active: bool):
        # 1. Insertar en BD origen
        result = self.repo.create(titulo, fecha, is_active)
        breakpoint()
        new_id = result["id"] if result else str(uuid.uuid4())
        # 2. Publicar evento CDC
        publish_change("INSERT", {"id_referencia": new_id, "titulo": titulo, "fecha": fecha, "is_active": is_active})
        return {"id": new_id}

    def actualizar(self, id: int, titulo: str, fecha: str, is_active: bool):
        # 1. Obtener datos previos (opcional, para enviar ambos estados)
        old = self.repo.get_by_id(id)
        if not old:
            raise ValueError("Publicación no existe")
        # 2. Actualizar
        self.repo.update(id, titulo, fecha, is_active)
        # 3. Publicar evento
        publish_change("UPDATE", {"id": id, "titulo": titulo, "fecha": fecha, "is_active": is_active})
        return True

    def eliminar(self, id: int):
        old = self.repo.get_by_id(id)
        if not old:
            raise ValueError("Publicación no existe")
        self.repo.delete(id)
        publish_change("DELETE", {"id": id})
        return True
