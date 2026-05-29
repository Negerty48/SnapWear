import os
import random
import glob
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Anuncios, Base
from app.ai_service import process_image_for_vector, detect_clothing
from app.azure_storage import upload_image, get_blob_service_client, CONTAINER_NAME
from dotenv import load_dotenv

load_dotenv()

DESCRIPTIONS = [
    "Prenda elegante para ocasiones especiales.",
    "Estilo casual perfecto para el día a día.",
    "Diseño moderno y exclusivo, ideal para combinar.",
    "Ropa cómoda y versátil de alta calidad.",
    "Tendencia de temporada que no puede faltar en tu armario.",
    "Básico imprescindible para cualquier outfit.",
    "Corte favorecedor y tejido suave.",
    "Look urbano y contemporáneo.",
    "Ideal para el verano, fresco y ligero.",
    "Perfecto para el invierno, cálido y confortable."
]

def reset_and_repopulate():
    print("=== STARTING CATALOG RESET ===")
    
    db = SessionLocal()
    
    # 1. Delete all from DB
    print("1. Deleting all records from database...")
    db.query(Anuncios).delete()
    db.commit()
    print("Database cleared.")
    
    # 2. Delete all blobs from Azure
    print("2. Deleting all images from Azure Blob Storage...")
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = container_client.list_blobs()
    blob_names = [b.name for b in blobs]
    if blob_names:
        for name in blob_names:
            container_client.delete_blob(name)
    print(f"Deleted {len(blob_names)} blobs.")
    
    # 3. Get images
    print("3. Fetching and shuffling test images...")
    img_dir = r"c:\Users\Alumno_AI\Desktop\SnapWear\data\DeepFashion2\deepfashion2_original_images\test\test\image"
    all_images = glob.glob(os.path.join(img_dir, "*.jpg"))
    random.shuffle(all_images)
    
    limit = 2500
    images_to_process = all_images[:limit]
    print(f"Selected {len(images_to_process)} images for processing.")
    
    # 4. Upload and vectorize
    print("4. Starting processing loop...")
    count = 0
    for idx, img_path in enumerate(images_to_process):
        try:
            with open(img_path, 'rb') as f:
                file_bytes = f.read()
                
            # Check if there is clothing
            detections = detect_clothing(file_bytes)
            if not detections:
                continue
                
            # Use the first detected clothing for the vector
            vector = process_image_for_vector(file_bytes, box_index=0)
            
            # Generate random data
            price = round(random.uniform(10.0, 45.0), 2)
            desc = random.choice(DESCRIPTIONS)
            filename = os.path.basename(img_path)
            
            # Upload to Azure
            image_url = upload_image(file_bytes, filename)
            
            # Save to DB
            new_anuncio = Anuncios(
                precio=price,
                descripcion=desc,
                imagen_url=image_url,
                vector_clip=vector,
                vendedor_id="auto_script"
            )
            db.add(new_anuncio)
            db.commit()
            
            count += 1
            if count % 10 == 0:
                print(f"Processed {count} / {limit} images...")
                
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            db.rollback()
            
    print(f"=== COMPLETED. Successfully added {count} items. ===")
    
if __name__ == "__main__":
    reset_and_repopulate()
