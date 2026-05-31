"""
FastAPI main application for SnapWear backend.
"""
import os
import requests
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, engine
from app.models import Anuncios
from app.schemas import AnuncioResponse, AnunciosListResponse
from app.ai_service import process_image_for_vector, detect_clothing
from app.azure_storage import upload_image

# Initialize FastAPI app
app = FastAPI(
    title="SnapWear Backend",
    description="API for SnapWear fashion e-commerce platform",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running"""
    return {"status": "ok", "message": "SnapWear Backend is running"}


# GET /anuncios - Retrieve all announcements
@app.get("/anuncios", response_model=AnunciosListResponse, tags=["Anuncios"])
async def get_all_anuncios(
    skip: int = 0,
    limit: int = 100,
    vendedor_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all announcements from the database.
    
    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum number of records to return (default: 100)
    - `vendedor_id`: Filter by seller ID - optional
    
    **Returns:**
    - `total`: Total number of announcements matching filters
    - `items`: List of announcement objects
    """
    try:
        # Build query
        query = db.query(Anuncios)
        
        # Apply filters if provided
        if vendedor_id:
            query = query.filter(Anuncios.vendedor_id == vendedor_id)
        
        # Count total
        total = query.count()
        
        # Apply pagination
        anuncios = query.offset(skip).limit(limit).all()
        
        return AnunciosListResponse(
            total=total,
            items=anuncios
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving announcements: {str(e)}"
        )


# GET /anuncios/{anuncio_id} - Retrieve a specific announcement
@app.get("/anuncios/{anuncio_id}", response_model=AnuncioResponse, tags=["Anuncios"])
async def get_anuncio(anuncio_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific announcement by ID.
    
    **Parameters:**
    - `anuncio_id`: Integer ID of the announcement
    
    **Returns:**
    - Single announcement object with all details including vector_clip
    """
    try:
        anuncio = db.query(Anuncios).filter(Anuncios.id == anuncio_id).first()
        
        if not anuncio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Announcement with ID {anuncio_id} not found"
            )
        
        return anuncio
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving announcement: {str(e)}"
        )


# GET /anuncios/{anuncio_id}/similares - Retrieve similar announcements
@app.get("/anuncios/{anuncio_id}/similares", response_model=AnunciosListResponse, tags=["Anuncios"])
async def get_anuncios_similares(anuncio_id: int, db: Session = Depends(get_db)):
    """
    Retrieve 3 similar announcements based on CLIP vector embeddings.
    """
    try:
        # Fetch the target announcement
        target = db.query(Anuncios).filter(Anuncios.id == anuncio_id).first()
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Announcement with ID {anuncio_id} not found"
            )
            
        if target.vector_clip is None:
            return AnunciosListResponse(total=0, items=[])
            
        # Find similar items using pgvector cosine distance
        similares = db.query(Anuncios)\
            .filter(Anuncios.id != anuncio_id)\
            .filter(Anuncios.vector_clip != None)\
            .order_by(Anuncios.vector_clip.cosine_distance(target.vector_clip))\
            .limit(3)\
            .all()
            
        return AnunciosListResponse(
            total=len(similares),
            items=similares
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving similar announcements: {str(e)}"
        )


# POST /anuncios - Create a new announcement
@app.post("/anuncios", response_model=AnuncioResponse, tags=["Anuncios"])
async def create_anuncio(
    precio: float = Form(...),
    descripcion: str = Form(""),
    box_index: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Create a new announcement with image upload and AI vectorization for a specific garment.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # 1. Process image with YOLO and FashionCLIP
        vector = process_image_for_vector(file_bytes, box_index=box_index)
        
        # 2. Upload to Azure Blob Storage
        image_url = upload_image(file_bytes, file.filename)
        
        # 3. Save to Database
        new_anuncio = Anuncios(
            precio=precio,
            descripcion=descripcion,
            imagen_url=image_url,
            vendedor_id="user_local", # Default user
            vector_clip=vector
        )
        db.add(new_anuncio)
        db.commit()
        db.refresh(new_anuncio)
        
        return new_anuncio
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating announcement: {str(e)}"
        )


# POST /ai/detect - Detect clothing items in an image
@app.post("/ai/detect", tags=["AI"])
async def ai_detect_clothing(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    """
    Detects clothing items in an image and returns them as base64 cropped images.
    """
    try:
        if file:
            file_bytes = await file.read()
        elif url:
            resp = requests.get(url)
            resp.raise_for_status()
            file_bytes = resp.content
        else:
            raise HTTPException(status_code=400, detail="Must provide either file or url")
            
        detections = detect_clothing(file_bytes)
        return {"detections": detections}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting clothing: {str(e)}"
        )


# POST /anuncios/buscar - Visual search by image or URL
@app.post("/anuncios/buscar", response_model=AnunciosListResponse, tags=["Anuncios"])
async def buscar_por_imagen(
    box_index: int = Form(0),
    file: UploadFile = File(None),
    url: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Find similar announcements using an uploaded image or URL without saving it to the database.
    Allows specifying which bounding box to use via box_index.
    Returns all results with similarity >= 0.5.
    """
    try:
        if file:
            file_bytes = await file.read()
        elif url:
            resp = requests.get(url)
            resp.raise_for_status()
            file_bytes = resp.content
        else:
            raise HTTPException(status_code=400, detail="Must provide either file or url")
        
        # Process image with YOLO and FashionCLIP to get the vector for the selected crop
        vector = process_image_for_vector(file_bytes, box_index=box_index)
        
        # Query pgvector for similar vectors, get top 100 to filter by similarity threshold
        similares_with_distance = db.query(
            Anuncios,
            Anuncios.vector_clip.cosine_distance(vector).label('distance')
        )\
            .filter(Anuncios.vector_clip != None)\
            .order_by(Anuncios.vector_clip.cosine_distance(vector))\
            .limit(100)\
            .all()
        
        # Filter by similarity threshold (0.5) and build response
        # Similarity = 1 - (distance / 2), where distance is cosine distance (0-2 range)
        items = []
        for anuncio, distance in similares_with_distance:
            similarity = 1 - (distance / 2)
            if similarity >= 0.8:
                # Create response object with similarity
                anuncio_dict = {
                    "id": anuncio.id,
                    "precio": float(anuncio.precio),
                    "imagen_url": anuncio.imagen_url,
                    "descripcion": anuncio.descripcion,
                    "vendedor_id": anuncio.vendedor_id,
                    "vector_clip": anuncio.vector_clip,
                    "similarity": round(similarity, 3)
                }
                items.append(anuncio_dict)
        
        return {
            "items": items,
            "total": len(items),
            "page": 1,
            "size": len(items),
            "pages": 1
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing visual search: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )
