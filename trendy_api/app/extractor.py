import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

class VectorizadorCLIP:
    def __init__(self):
        """Descarga/Carga el modelo de Hugging Face en la RAM."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "patrickjohncyh/fashion-clip"        
        self.processor = CLIPProcessor.from_pretrained(self.model_id)
        self.model = CLIPModel.from_pretrained(self.model_id).to(self.device)
        self.model.eval() # Modo evaluación, apaga el entrenamiento

    def obtener_embedding(self, imagen_pil):
        """
        Recibe un recorte de ropa (PIL) y devuelve un vector de 512 dimensiones 
        normalizado, listo para inyectar en la base de datos vectorial.
        """
        inputs = self.processor(images=imagen_pil, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            
        image_features_norm = F.normalize(image_features, p=2, dim=1)
        
        vector_lista = image_features_norm.squeeze().tolist()
        
        return vector_lista