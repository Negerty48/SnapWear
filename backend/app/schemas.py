"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class AnuncioBase(BaseModel):
    """Base schema for Anuncios"""
    precio: float = Field(..., gt=0, description="Precio del producto")
    imagen_url: str = Field(..., description="URL de la imagen del producto")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del anuncio")
    vendedor_id: Optional[str] = Field(None, description="ID del vendedor")


class AnuncioCreate(AnuncioBase):
    """Schema for creating a new Anuncio"""
    pass


class AnuncioUpdate(BaseModel):
    """Schema for updating an Anuncio"""
    precio: Optional[float] = Field(None, gt=0)
    imagen_url: Optional[str] = Field(None)
    descripcion: Optional[str] = Field(None)
    vendedor_id: Optional[str] = Field(None)


class AnuncioResponse(AnuncioBase):
    """Schema for Anuncio response"""
    id: int
    vector_clip: Optional[List[float]] = Field(None, description="Vector de embedding CLIP (512 dimensiones)")
    similarity: Optional[float] = Field(None, description="Puntuación de similitud (0-1, donde 1 es idéntico)")

    class Config:
        from_attributes = True


class AnunciosListResponse(BaseModel):
    """Schema for list of Anuncios"""
    total: int = Field(..., description="Total de anuncios")
    items: List[AnuncioResponse] = Field(..., description="Lista de anuncios")

    class Config:
        from_attributes = True
