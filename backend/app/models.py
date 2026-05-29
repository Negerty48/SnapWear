"""
SQLAlchemy models for SnapWear database.
"""
from sqlalchemy import Column, Integer, String, Numeric
from pgvector.sqlalchemy import Vector
from app.database import Base


class Anuncios(Base):
    """
    Model for advertisements/announcements in the platform.
    Matches the existing PostgreSQL schema exactly.
    """
    __tablename__ = "anuncios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    precio = Column(Numeric(precision=10, scale=2), nullable=False)
    vector_clip = Column(Vector(512), nullable=True)
    vendedor_id = Column(String, nullable=True, index=True)
    imagen_url = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)

    def __repr__(self):
        return f"<Anuncios(id={self.id}, precio={self.precio}, vendedor_id='{self.vendedor_id}')>"
