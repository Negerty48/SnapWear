"""
SnapWear Backend Application
"""
from app.database import Base, get_db
from app.models import Anuncios

__all__ = ["Base", "get_db", "Anuncios"]
