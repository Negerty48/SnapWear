from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from app.config import DATABASE_URL, MAX_SEARCH_RESULTS

# ==========================================
# MOTOR DE BASE DE DATOS
# ==========================================
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ==========================================
# MODELO DE DATOS
# ==========================================
class AnuncioPrenda(Base):
    __tablename__ = "anuncios"

    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(String, index=True)
    precio = Column(Float, nullable=False)
    imagen_url = Column(String, nullable=False)
    vector_clip = Column(Vector(512))

# Nota: En producción, crearíamos la tabla y la extensión 'vector' con migraciones (Alembic).
# Aquí forzamos su creación si no existe para facilitar el desarrollo.
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
Base.metadata.create_all(bind=engine)

# ==========================================
# BÚSQUEDA VECTORIAL
# ==========================================
def buscar_prendas_similares(vector_usuario: list, limite: int = MAX_SEARCH_RESULTS):
    """
    Recibe el vector de la foto del usuario y busca en la BBDD las prendas más parecidas.
    Usa el operador '<->' de pgvector que calcula la Distancia del Coseno.
    """
    db = SessionLocal()
    try:
        vector_str = str(vector_usuario)
        
        query = text(f"""
            SELECT id, precio, imagen_url, 
                   1 - (vector_clip <-> '{vector_str}') AS similitud 
            FROM anuncios 
            ORDER BY vector_clip <-> '{vector_str}' 
            LIMIT :limite
        """)
        
        resultados = db.execute(query, {"limite": limite}).fetchall()
        
        lista_respuesta = []
        for fila in resultados:
            lista_respuesta.append({
                "id_prenda": fila.id,
                "precio": fila.precio,
                "imagen_url": fila.imagen_url,
                "similitud": round(fila.similitud, 4)
            })
            
        return lista_respuesta
    finally:
        db.close()