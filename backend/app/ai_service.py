import io
import os
import torch
from PIL import Image
from ultralytics import YOLO
from transformers import CLIPProcessor, CLIPModel
import logging

logger = logging.getLogger(__name__)

# Config
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
YOLO_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "notebooks", "yolov8n.pt")

yolo_model = None
clip_model = None
clip_processor = None

def init_ai_models():
    global yolo_model, clip_model, clip_processor
    
    if yolo_model is None:
        logger.info(f"Loading YOLO model from {YOLO_MODEL_PATH}")
        try:
            yolo_model = YOLO(YOLO_MODEL_PATH)
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise e
            
    if clip_model is None:
        logger.info("Loading FashionCLIP model")
        clip_model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip").to(DEVICE)
        clip_processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")
        clip_model.eval()

def process_image_for_vector(image_bytes: bytes) -> list[float]:
    """
    Receives image bytes, crops the clothing using YOLO, 
    and returns a 512-dim embedding using FashionCLIP.
    """
    if yolo_model is None or clip_model is None:
        init_ai_models()
        
    # Open image
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    width, height = img.size
    
    # 1. Crop with YOLO
    logger.info("Running YOLO detection")
    results = yolo_model(img, conf=0.15, verbose=False)
    cajas = results[0].boxes
    
    # Filter class 0
    cajas_ropa = [box for box in cajas if int(box.cls[0]) == 0]
    
    if len(cajas_ropa) == 0:
        logger.info("No clothing detected, using full image")
        img_cropped = img
    else:
        logger.info(f"Detected {len(cajas_ropa)} clothing items, using the first one")
        box_elegida = cajas_ropa[0]
        x1, y1, x2, y2 = box_elegida.xyxy[0].cpu().numpy()
        
        # 5% padding
        pad_x = (x2 - x1) * 0.05
        pad_y = (y2 - y1) * 0.05
        x1_p, y1_p = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2_p, y2_p = min(width, x2 + pad_x), min(height, y2 + pad_y)
        
        img_cropped = img.crop((x1_p, y1_p, x2_p, y2_p))
        
    # 2. Extract Vector with FashionCLIP
    logger.info("Extracting FashionCLIP embedding")
    inputs = clip_processor(images=img_cropped, return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        vision_outputs = clip_model.vision_model(**inputs)
        image_embeds = clip_model.visual_projection(vision_outputs.pooler_output)
        embedding = image_embeds.cpu().numpy().flatten()
        
    return embedding.tolist()
