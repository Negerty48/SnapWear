from ultralytics import YOLO
from PIL import Image
from app.config import YOLO_WEIGHTS_PATH, YOLO_CONFIDENCE

class RopaDetector:
    def __init__(self):
        """Carga el modelo YOLO en la RAM al arrancar la API."""
        self.model = YOLO(YOLO_WEIGHTS_PATH)

    def detectar_y_recortar(self, imagen_pil, id_prenda=0):
        """
        Recibe una imagen PIL y devuelve solo el recorte de la tela elegida.
        Mantiene las cajas anidadas (Overlapping) por decisión de producto (UX).
        """
        width, height = imagen_pil.size
        
        resultados = self.model(imagen_pil, conf=YOLO_CONFIDENCE, verbose=False)
        
        cajas_ropa = [box for box in resultados[0].boxes if int(box.cls[0]) == 0]
        
        if len(cajas_ropa) == 0:
            # Fallback 1: Si no hay ropa, mandamos la foto entera
            return imagen_pil
            
        if id_prenda < 0 or id_prenda >= len(cajas_ropa):
            # Fallback 2: Si piden un ID que no existe, forzamos el 0
            id_prenda = 0
            
        box_elegida = cajas_ropa[id_prenda]
        x1, y1, x2, y2 = box_elegida.xyxy[0].tolist()
        
        pad_x, pad_y = (x2 - x1) * 0.05, (y2 - y1) * 0.05
        x1_p, y1_p = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2_p, y2_p = min(width, x2 + pad_x), min(height, y2 + pad_y)
        
        return imagen_pil.crop((x1_p, y1_p, x2_p, y2_p))