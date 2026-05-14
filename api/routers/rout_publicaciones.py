# api/routes/publicaciones.py
from fastapi import APIRouter, HTTPException
from application.publicaciones_service import PublicacionesService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/publicaciones", tags=["publicaciones"])

class PublicacionCreate(BaseModel):
    titulo: str
    fecha: datetime
    is_active: bool = True

class PublicacionUpdate(BaseModel):
    titulo: str
    fecha: datetime
    is_active: bool

@router.post("/")
def crear(pub: PublicacionCreate):
    service = PublicacionesService()
    fecha_str = pub.fecha.strftime("%Y-%m-%d %H:%M:%S")
    result = service.crear(pub.titulo, fecha_str, pub.is_active)
    return result

@router.put("/{id}")
def actualizar(id: int, pub: PublicacionUpdate):
    service = PublicacionesService()
    fecha_str = pub.fecha.strftime("%Y-%m-%d %H:%M:%S")
    service.actualizar(id, pub.titulo, fecha_str, pub.is_active)
    return {"ok": True}

@router.delete("/{id}")
def eliminar(id: int):
    service = PublicacionesService()
    service.eliminar(id)
    return {"ok": True}
