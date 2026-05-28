import time
import io
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import RespuestaBusqueda
from app.detector import RopaDetector
from app.extractor import VectorizadorCLIP
from app.database import buscar_prendas_similares

app = FastAPI(
    title="Trendy Market AI API", 
    description="Motor de búsqueda visual interactivo para ropa de segunda mano.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = RopaDetector()
extractor = VectorizadorCLIP()

@app.get("/")
def health_check():
    """Endpoint básico para que Azure sepa que el servidor está vivo."""
    return {"status": "ok", "mensaje": "API de Trendy Market operativa 🚀"}

@app.post("/buscar", response_model=RespuestaBusqueda)
async def endpoint_buscar_ropa(
    foto: UploadFile = File(...), 
    id_prenda: int = Form(0)
):
    """
    Recibe la foto del usuario y el ID de la prenda a buscar, y devuelve 
    los 3 artículos más similares del catálogo.
    """
    t0 = time.time()
    
    try:
        # 1. Leer la imagen subida desde la memoria (sin guardarla en disco)
        imagen_bytes = await foto.read()
        imagen_pil = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")
        
        # 2. IA (Visión): YOLO recorta la prenda elegida
        img_recortada = detector.detectar_y_recortar(imagen_pil, id_prenda)
        
        # 3. IA (Semántica): FashionCLIP saca el vector matemático
        vector = extractor.obtener_embedding(img_recortada)
        
        # 4. Base de Datos: Consulta ultrarrápida a PostgreSQL con pgvector
        resultados_db = buscar_prendas_similares(vector)
        
        tiempo_total = (time.time() - t0) * 1000
        
        # 5. Devolver la respuesta formateada con Pydantic
        return {
            "mensaje": "Búsqueda completada con éxito",
            "tiempo_procesamiento_ms": round(tiempo_total, 2),
            "resultados": resultados_db
        }
        
    except Exception as e:
        # Si algo falla (ej. la imagen está corrupta), evitamos que el servidor colapse
        raise HTTPException(status_code=500, detail=f"Error procesando la búsqueda: {str(e)}")