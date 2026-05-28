from pydantic import BaseModel, Field
from typing import List

# ==========================================
# ESQUEMAS DE RESPUESTA (Lo que le enviamos al móvil)
# ==========================================

class PrendaRecomendada(BaseModel):
    """Estructura de cada prenda individual que encontramos en la BBDD"""
    id_prenda: int = Field(..., description="ID único de la prenda en la base de datos")
    similitud: float = Field(..., description="Porcentaje de similitud visual (0 a 1)")
    precio: float = Field(..., description="Precio de la prenda en euros")
    imagen_url: str = Field(..., description="URL de la imagen alojada en Azure Blob Storage")

class RespuestaBusqueda(BaseModel):
    """El paquete completo que recibe la App del móvil"""
    mensaje: str = Field(..., description="Estado de la petición (ej. 'Búsqueda exitosa')")
    tiempo_procesamiento_ms: float = Field(..., description="Milisegundos que tardó todo el pipeline")
    resultados: List[PrendaRecomendada] = Field(default_factory=list, description="Lista de las prendas más parecidas")