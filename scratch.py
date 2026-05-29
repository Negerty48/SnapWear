import os
import time
import json
import numpy as np
import kagglehub
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# Configuramos el dispositivo (GPU si está disponible, si no CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")

import os
import kagglehub
import shutil

destino = "../data"

if os.path.exists(destino) and len(os.listdir(destino)) > 0:
    print(f"✅ El dataset ya está disponible en: {destino}. Saltando descarga.")
else:        
    # Descarga desde Kaggle
    path_origen = kagglehub.dataset_download("thusharanair/deepfashion2-original-with-dataframes")
    print(f"Dataset descargado temporalmente en: {path_origen}")
    
    # Mover al destino final
    print(f"Moviendo los archivos a la carpeta: {destino}...")
    os.makedirs(destino, exist_ok=True) # Nos aseguramos de que la carpeta contenedora exista
    shutil.copytree(path_origen, destino, dirs_exist_ok=True)
    print(f"🎉 Dataset listo y organizado en: {destino}")

resnet_weights = ResNet50_Weights.DEFAULT
resnet = resnet50(weights=resnet_weights)
# Extraemos todas las capas menos la última (Fully Connected)
resnet = torch.nn.Sequential(*list(resnet.children())[:-1]).to(device)
resnet.eval() # Modo evaluación
resnet_preprocess = resnet_weights.transforms()

# Usamos el modelo preentrenado 'patrickjohncyh/fashion-clip'
clip_model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip").to(device)
clip_processor = CLIPProcessor.from_pretrained("patrickjohncyh/fashion-clip")
clip_model.eval()

print("Modelos cargados correctamente")

def get_resnet_embedding(image_path):
    img = Image.open(image_path).convert('RGB')
    # Preprocesamiento y paso al dispositivo
    img_tensor = resnet_preprocess(img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = resnet(img_tensor).cpu().numpy().flatten()
    return embedding

def get_clip_embedding(image_path):
    img = Image.open(image_path).convert('RGB')
    
    # Preprocesamiento de CLIP (solo imagen)
    inputs = clip_processor(images=img, return_tensors="pt").to(device)
    
    with torch.no_grad():
        # 1. Pasamos la imagen SOLO por el módulo visual (ignorando el de texto)
        vision_outputs = clip_model.vision_model(**inputs)
        
        # 2. Tomamos la salida agrupada (pooler_output) y la proyectamos a 512 dimensiones
        image_embeds = clip_model.visual_projection(vision_outputs.pooler_output)
        
        # 3. Lo pasamos a CPU, lo convertimos en array de numpy y lo aplanamos a 1D
        embedding = image_embeds.cpu().numpy().flatten()
            
    return embedding

# Tomamos solo las primeras 5 imágenes para la prueba rápida
train_images_dir = "../data/DeepFashion2/deepfashion2_original_images/train/image"
sample_images = [os.path.join(train_images_dir, f) for f in os.listdir(train_images_dir) if f.endswith('.jpg')][:5]

print("--- TEST DE LATENCIA ---")
# Test ResNet
start_resnet = time.time()
resnet_embeddings = [get_resnet_embedding(img) for img in sample_images]
time_resnet = (time.time() - start_resnet) / len(sample_images)
print(f"ResNet50     -> Tiempo medio por imagen: {time_resnet:.4f} segundos | Dimensión: {resnet_embeddings[0].shape[0]}")

# Test CLIP
start_clip = time.time()
clip_embeddings = [get_clip_embedding(img) for img in sample_images]
time_clip = (time.time() - start_clip) / len(sample_images)
print(f"FashionCLIP -> Tiempo medio por imagen: {time_clip:.4f} segundos | Dimensión: {clip_embeddings[0].shape[0]}")

# Usamos la primera imagen como "Consulta" y el resto como "Catálogo"
query_resnet = resnet_embeddings[0].reshape(1, -1)
catalog_resnet = np.array(resnet_embeddings[1:])

query_clip = clip_embeddings[0].reshape(1, -1)
catalog_clip = np.array(clip_embeddings[1:])

# Calculamos similitud del coseno (valores entre -1 y 1, donde 1 es idéntico)
sim_resnet = cosine_similarity(query_resnet, catalog_resnet)[0]
sim_clip = cosine_similarity(query_clip, catalog_clip)[0]

print("Resultados de Similitud (Query vs Catálogo):")
for i in range(len(sim_resnet)):
    print(f"Imagen {i+1} -> Similitud ResNet: {sim_resnet[i]:.3f} | Similitud FashionCLIP: {sim_clip[i]:.3f}")

import os
import json
import shutil
import numpy as np

def get_style_id(image_path, annos_dir):
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    json_path = os.path.join(annos_dir, base_name + '.json')
    
    if not os.path.exists(json_path):
        return None
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    for key, value in data.items():
        if key.startswith('item') and type(value) == dict:
            if 'style' in value:
                return value['style']
    return None

poc_output_dir = "../data/catalog_saved"
poc_images_dir = os.path.join(poc_output_dir, "images")

# Archivos donde guardaremos las matrices y las rutas
paths_json_file = os.path.join(poc_output_dir, "valid_image_paths.json")
styles_npy_file = os.path.join(poc_output_dir, "styles.npy")
resnet_npy_file = os.path.join(poc_output_dir, "resnet_vecs.npy")
clip_npy_file = os.path.join(poc_output_dir, "clip_vecs.npy")

# COMPROBACIÓN: Si ya se procesó en el pasado, lo cargamos directamente en memoria
if os.path.exists(poc_output_dir) and os.path.exists(styles_npy_file):
    print("⚡ ¡Catálogo PoC detectado en disco! Cargando imágenes y vectores almacenados...")
    
    resnet_eval_vecs = np.load(resnet_npy_file)
    clip_eval_vecs = np.load(clip_npy_file)
    styles = np.load(styles_npy_file)
    
    with open(paths_json_file, 'r') as f:
        valid_image_paths = json.load(f)
        
    print(f"✅ Éxito: {len(styles)} elementos listos para usar.")

else:
    print("⏳ No se encontraron datos previos. Creando catálogo desde cero...")
    os.makedirs(poc_images_dir, exist_ok=True)

    # Cargamos todas las rutas de imágenes originales disponibles
    train_images_dir = "../data/DeepFashion2/deepfashion2_original_images/train/image"
    all_image_paths = [os.path.join(train_images_dir, f) for f in os.listdir(train_images_dir) if f.endswith('.jpg')]
    train_annos_dir = "../data/DeepFashion2/deepfashion2_original_images/train/annos"
    
    resnet_eval_vecs_list = []
    clip_eval_vecs_list = []
    styles_list = []
    valid_image_paths = []

    TARGET_SIZE = 1500 

    for img_path in all_image_paths:
        style_id = get_style_id(img_path, train_annos_dir)
        
        if style_id is not None:
            # 1. Definimos la nueva ruta local dentro de nuestra carpeta PoC
            nombre_archivo = os.path.basename(img_path)
            nueva_ruta_img = os.path.join(poc_images_dir, nombre_archivo)
            
            # 2. Copiamos físicamente la imagen a la nueva carpeta
            shutil.copy(img_path, nueva_ruta_img)
            
            # 3. Extraemos los vectores usando la NUEVA ruta limpia de la imagen
            resnet_eval_vecs_list.append(get_resnet_embedding(nueva_ruta_img))
            clip_eval_vecs_list.append(get_clip_embedding(nueva_ruta_img))
            styles_list.append(style_id)
            valid_image_paths.append(nueva_ruta_img)
            
        if len(styles_list) >= TARGET_SIZE:
            break

    # Convertimos a arrays de NumPy
    resnet_eval_vecs = np.array(resnet_eval_vecs_list)
    clip_eval_vecs = np.array(clip_eval_vecs_list)
    styles = np.array(styles_list)

    # 4. GUARDAR EN DISCO TODO LO PROCESADO
    print("💾 Guardando imágenes, vectores y metadatos en el disco...")
    np.save(resnet_npy_file, resnet_eval_vecs)
    np.save(clip_npy_file, clip_eval_vecs)
    np.save(styles_npy_file, styles)
    
    with open(paths_json_file, 'w') as f:
        json.dump(valid_image_paths, f)
        
    print(f"🎉 Catálogo creado en '{poc_output_dir}' con {len(styles)} imágenes.")

# =====================================================================
# MÉTRICAS DE CALIDAD DE LA MUESTRA
# =====================================================================
unique_styles, counts = np.unique(styles, return_counts=True)
pairs_count = sum(counts > 1)
print(f"Estilos únicos en el catálogo: {len(unique_styles)}")
print(f"Prendas que tienen al menos una pareja para buscar: {pairs_count}")

def calculate_accuracy(embeddings, labels, top_k=3):
    aciertos = 0
    total_consultas = 0
    
    # Comparamos cada imagen contra TODAS las demás
    sim_matrix = cosine_similarity(embeddings)
    
    for i in range(len(labels)):
        query_label = labels[i]
        
        # Buscamos si hay alguna otra prenda con este mismo estilo en la lista
        # (Si es la única prenda de este estilo, la ignoramos porque no hay pareja que encontrar)
        if np.sum(labels == query_label) > 1:
            total_consultas += 1
            
            # Ordenamos los índices por similitud de mayor a menor
            # Descartamos el índice 'i' (la propia imagen siendo comparada consigo misma)
            sim_scores = sim_matrix[i].copy()
            sim_scores[i] = -1 # Le damos un valor negativo para que no sea la primera
            
            # Cogemos los índices de los 'top_k' resultados con mayor puntuación
            top_indices = np.argsort(sim_scores)[-top_k:][::-1]
            top_labels = labels[top_indices]
            
            # Si el estilo correcto está entre los devueltos, es un ACIERTO
            if query_label in top_labels:
                aciertos += 1
                
    if total_consultas == 0:
        return 0.0, 0
    return (aciertos / total_consultas) * 100, total_consultas

print("=== RESULTADOS DEFINITIVOS DE PRECISIÓN ===")

# Test Top-1 (El modelo pone la pareja exacta como 1º resultado)
resnet_acc_1, valid_queries = calculate_accuracy(resnet_eval_vecs, styles, top_k=1)
clip_acc_1, _ = calculate_accuracy(clip_eval_vecs, styles, top_k=1)

print(f"Top-1 Accuracy (Consultas válidas: {valid_queries})")
print(f" -> ResNet50:        {resnet_acc_1:.2f}%")
print(f" -> FashionCLIP:     {clip_acc_1:.2f}%\n")

# Test Top-3 (El modelo pone la pareja exacta entre los 3 primeros)
resnet_acc_3, _ = calculate_accuracy(resnet_eval_vecs, styles, top_k=3)
clip_acc_3, _ = calculate_accuracy(clip_eval_vecs, styles, top_k=3)

print(f"Top-3 Accuracy")
print(f" -> ResNet50:        {resnet_acc_3:.2f}%")
print(f" -> FashionCLIP:     {clip_acc_3:.2f}%")

import matplotlib.pyplot as plt

def show_results_visually(query_index, embeddings_modelA, embeddings_modelB, image_paths, top_k=3):    
    # Calculamos similitudes para esta consulta específica
    query_A = embeddings_modelA[query_index].reshape(1, -1)
    sim_A = cosine_similarity(query_A, embeddings_modelA)[0]
    sim_A[query_index] = -1 # Ignorar la propia imagen
    top_indices_A = np.argsort(sim_A)[-top_k:][::-1]
    
    query_B = embeddings_modelB[query_index].reshape(1, -1)
    sim_B = cosine_similarity(query_B, embeddings_modelB)[0]
    sim_B[query_index] = -1
    top_indices_B = np.argsort(sim_B)[-top_k:][::-1]

    # Configuramos el gráfico (Matplotlib)
    fig, axes = plt.subplots(3, top_k + 1, figsize=(15, 10))
    fig.suptitle(f"Análisis Visual - Consulta #{query_index}", fontsize=16)
    
    # Mostrar Query
    ax_query = axes[0, 0]
    ax_query.imshow(Image.open(image_paths[query_index]))
    ax_query.set_title("IMAGEN SUBIDA\n(Query)")
    ax_query.axis('off')
    
    # Ocultar el resto de la primera fila
    for i in range(1, top_k + 1):
        axes[0, i].axis('off')

    # Fila ResNet
    axes[1, 0].text(0.5, 0.5, 'Resultados\nResNet50', fontsize=14, ha='center', va='center')
    axes[1, 0].axis('off')
    for i, idx in enumerate(top_indices_A):
        axes[1, i+1].imshow(Image.open(image_paths[idx]))
        axes[1, i+1].set_title(f"Top {i+1} (Sim: {sim_A[idx]:.2f})")
        axes[1, i+1].axis('off')

    # Fila CLIP
    axes[2, 0].text(0.5, 0.5, 'Resultados\nFashionCLIP', fontsize=14, ha='center', va='center')
    axes[2, 0].axis('off')
    for i, idx in enumerate(top_indices_B):
        axes[2, i+1].imshow(Image.open(image_paths[idx]))
        axes[2, i+1].set_title(f"Top {i+1} (Sim: {sim_B[idx]:.2f})")
        axes[2, i+1].axis('off')

    plt.tight_layout()
    plt.show()

# Vamos a buscar una imagen donde ResNet y CLIP no estén de acuerdo en el Top 1
# o simplemente ver las primeras 3 imágenes de nuestra muestra
print("Generando visualizaciones de comprobación...")
for i in range(3):
    show_results_visually(i, resnet_eval_vecs, clip_eval_vecs, valid_image_paths, top_k=3)

import os
import json
import shutil
from PIL import Image

yolo_dataset_dir = "../data/yolo_fashion"
os.makedirs(os.path.join(yolo_dataset_dir, "images/train"), exist_ok=True)
os.makedirs(os.path.join(yolo_dataset_dir, "labels/train"), exist_ok=True)

imagenes_procesadas = 0
prendas_etiquetadas = 0

for img_path in valid_image_paths:
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    json_path = os.path.join(train_annos_dir, base_name + '.json')
    
    if not os.path.exists(json_path):
        continue
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    with Image.open(img_path) as img:
        img_width, img_height = img.size
        
    lineas_etiquetas = []
    
    # Recorremos TODAS las llaves del JSON
    for key, value in data.items():
        if key.startswith('item') and type(value) == dict and 'bounding_box' in value:
            x1, y1, x2, y2 = value['bounding_box']
            
            x_center = ((x1 + x2) / 2) / img_width
            y_center = ((y1 + y2) / 2) / img_height
            box_width = (x2 - x1) / img_width
            box_height = (y2 - y1) / img_height
            
            # Guardamos cada coordenada en la lista
            lineas_etiquetas.append(f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")
            prendas_etiquetadas += 1
            
    # Solo copiamos la imagen y creamos el txt si hemos encontrado ropa válida
    if len(lineas_etiquetas) > 0:
        destino_img = os.path.join(yolo_dataset_dir, "images/train", f"{base_name}.jpg")
        if not os.path.exists(destino_img):
            shutil.copy(img_path, destino_img)
        
        txt_path = os.path.join(yolo_dataset_dir, "labels/train", f"{base_name}.txt")
        # Escribimos TODAS las prendas de esta imagen en su archivo .txt
        with open(txt_path, 'w') as f_txt:
            f_txt.writelines(lineas_etiquetas)
            
        imagenes_procesadas += 1

print(f"¡Listo! Dataset Multi-Prenda preparado.")
print(f"Total imágenes: {imagenes_procesadas}")
print(f"Total prendas etiquetadas: {prendas_etiquetadas}")

import yaml

# Creamos el archivo fashion.yaml
yaml_path = os.path.join(yolo_dataset_dir, "fashion.yaml")

yaml_data = {
    'path': os.path.abspath(yolo_dataset_dir), 
    'train': 'images/train',                    # Carpeta de entrenamiento
    'val': 'images/train',                      # (Para la PoC usamos las mismas para validar)
    'names': {0: 'ropa'}                        # Solo tenemos una clase
}

with open(yaml_path, 'w') as f:
    yaml.dump(yaml_data, f, default_flow_style=False)

print(f"Archivo de configuración creado en: {yaml_path}")

from ultralytics import YOLO

# Cargamos el modelo base
model_to_train = YOLO('yolov8n.pt')

# Lanzamos el entrenamiento
results = model_to_train.train(
    data=yaml_path,
    epochs=25,
    imgsz=640,
    batch=16,
    name='trendy_yolo'
)

print("¡Entrenamiento finalizado! Tu modelo experto en ropa está guardado en la carpeta 'runs/detect/trendy_yolo/weights/best.pt'")

yolo_model = YOLO("../runs/detect/trendy_yolo/weights/best.pt")

def obtener_recorte_elegido(ruta_img, id_prenda = 0, conf_umbral=0.15):
    img = Image.open(ruta_img).convert('RGB')
    width, height = img.size
    
    # YOLO hace la inferencia
    resultados = yolo_model(img, conf=conf_umbral, verbose=False)
    cajas = resultados[0].boxes
    
    # Filtramos para quedarnos solo con las cajas que son "ropa" (Clase 0)
    cajas_ropa = [box for box in cajas if int(box.cls[0]) == 0]
    
    # Caso 1: YOLO no ve nada de ropa
    if len(cajas_ropa) == 0:        
        return img
        
    # Caso 2: El usuario pide un ID que no existe (ej. pide la 2 pero solo hay 0 y 1)
    if id_prenda >= len(cajas_ropa):        
        id_prenda = 0
        
    # Extraemos las coordenadas de la prenda elegida
    box_elegida = cajas_ropa[id_prenda]
    x1, y1, x2, y2 = box_elegida.xyxy[0].cpu().numpy()
    
    # Añadimos un 5% de margen (padding) para no cortar los bordes justos
    pad_x = (x2 - x1) * 0.05
    pad_y = (y2 - y1) * 0.05
    x1_p, y1_p = max(0, x1 - pad_x), max(0, y1 - pad_y)
    x2_p, y2_p = min(width, x2 + pad_x), min(height, y2 + pad_y)
    
    # Devolvemos el recorte exacto
    return img.crop((x1_p, y1_p, x2_p, y2_p))

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# 1. Definimos la ruta y cargamos la lista de imágenes
carpeta_imagenes = "../data/catalog_saved/images"
valid_image_paths = [os.path.join(carpeta_imagenes, f) for f in os.listdir(carpeta_imagenes) if f.endswith('.jpg')]

# Seleccionamos las imágenes de prueba
indices_prueba = [8, 17, 24] 

fig, axes = plt.subplots(1, len(indices_prueba), figsize=(15, 6))
fig.suptitle("Detección Multi-Prenda: Identificando opciones con YOLOv8", fontsize=16, fontweight='bold', y=1.05)

# Si solo hay una imagen, axes no es un array, así que lo forzamos a lista para evitar errores
if len(indices_prueba) == 1:
    axes = [axes]

for col, idx in enumerate(indices_prueba):
    ruta_img = valid_image_paths[idx]
    img_original = Image.open(ruta_img).convert('RGB')
    
    # YOLO analiza la imagen (usamos conf=0.15 para que pille todo)
    resultados = yolo_model(img_original, conf=0.15, verbose=False)
    cajas = resultados[0].boxes
    
    ax = axes[col]
    ax.imshow(img_original)
    ax.set_title(f"Imagen #{idx}\n{len(cajas)} prendas detectadas", color='blue')
    ax.axis('off')
    
    # Definimos unos colores llamativos para diferenciar las prendas
    colores = ['red', 'cyan', 'lime', 'magenta', 'yellow']
    
    # Dibujamos cada caja detectada
    for i, box in enumerate(cajas):
        if int(box.cls[0]) == 0: # Clase 0 = Ropa
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            color = colores[i % len(colores)]
            
            # Dibujamos el rectángulo
            rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=3, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            
            # Ponemos el numerito arriba a la izquierda de la caja
            ax.text(x1, y1 - 10, f"Prenda #{i}", color='black', backgroundcolor=color, 
                    fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
from PIL import Image

indices_prueba = [8, 17, 24] 
seleccion_usuario = 1  

fig, axes = plt.subplots(len(indices_prueba), 2, figsize=(10, 5 * len(indices_prueba)))
fig.suptitle(f"Simulación de App: Prueba de Seguridad (Buscando ID: {seleccion_usuario})", fontsize=16, fontweight='bold', y=1.02)

if len(indices_prueba) == 1:
    axes = [axes]

for row, idx in enumerate(indices_prueba):
    ruta_prueba = valid_image_paths[idx]
        
    recorte_final = obtener_recorte_elegido(ruta_prueba, id_prenda = seleccion_usuario)
    
    # 1. Foto original
    img_orig = Image.open(ruta_prueba)
    axes[row, 0].imshow(img_orig)
    axes[row, 0].set_title(f"Imagen #{idx} - Original", color='blue')
    axes[row, 0].axis('off')
    
    # 2. El recorte extraído
    axes[row, 1].imshow(recorte_final)    
    axes[row, 1].set_title(f"Recorte Devuelto (Intento ID: {seleccion_usuario})", color='green')
    axes[row, 1].axis('off')

plt.tight_layout()
plt.show()

import faiss
import time
import numpy as np

# Nos aseguramos de que los datos son del tipo float32 (requisito estricto de FAISS)
vectores_base = clip_eval_vecs.astype('float32')

# Normalizamos los vectores
faiss.normalize_L2(vectores_base)

# Creamos el índice vectorial
dimensiones = vectores_base.shape[1] # 512
indice_faiss = faiss.IndexFlatIP(dimensiones)

# Inyectamos nuestro catálogo (1.500 imágenes) en el índice
indice_faiss.add(vectores_base)

print(f"✅ Índice creado con éxito.")
print(f"📏 Dimensiones por vector: {dimensiones}")
print(f"📦 Total de prendas indexadas: {indice_faiss.ntotal}")

print("Simulando búsqueda de usuario en tiempo real...")

# Simulamos que el usuario sube la primera imagen válida de nuestra lista
vector_usuario = clip_eval_vecs[0:1].astype('float32') 
faiss.normalize_L2(vector_usuario) # Normalizamos

start_time = time.time()

# Buscamos el Top 3 (k=3)
k = 3 
distancias, indices_resultados = indice_faiss.search(vector_usuario, k)

end_time = time.time()

tiempo_busqueda_ms = (end_time - start_time) * 1000

print(f"\n⚡ Tiempo de búsqueda en FAISS: {tiempo_busqueda_ms:.4f} milisegundos")
print(f"🏆 Top 3 IDs de imágenes encontradas: {indices_resultados[0]}")
print(f"🎯 Puntuación de similitud: {distancias[0]}")

import matplotlib.pyplot as plt

# Seleccionamos un índice de prueba
query_idx = 12

# 1. Recuperamos la ruta de la imagen original del usuario
ruta_usuario = valid_image_paths[query_idx]

# 2. Preparamos su vector para FAISS
vector_usuario = clip_eval_vecs[query_idx:query_idx+1].astype('float32')
faiss.normalize_L2(vector_usuario)

# 3. FAISS hace la búsqueda (Pedimos k=4 por si el primero es la idéntica)
k_search = 4
distancias, indices_resultados = indice_faiss.search(vector_usuario, k_search)

# 4. FILTRO: Quitamos la foto idéntica para simular un usuario real
top_3_limpio = []
for idx_catalogo, sim in zip(indices_resultados[0], distancias[0]):
    # Solo guardamos el resultado si no es exactamente la misma foto que subimos
    if idx_catalogo != query_idx: 
        top_3_limpio.append((idx_catalogo, sim))
    
    # Paramos en cuanto tengamos las 3 mejores recomendaciones distintas
    if len(top_3_limpio) == 3:
        break

# 5. Dibujamos los resultados
fig, axes = plt.subplots(1, 4, figsize=(15, 5))
fig.suptitle(f"BÚSQUEDA A ESCALA CON FAISS - Consulta #{query_idx}", fontsize=16, fontweight='bold')

# --- Columna 0: La Query del usuario ---
img_query = Image.open(ruta_usuario)
axes[0].imshow(img_query)
axes[0].set_title("IMAGEN SUBIDA\n(Query)", color='blue', fontweight='bold')
axes[0].axis('off')

# --- Columnas 1, 2 y 3: Los resultados del Índice FAISS ---
for rank, (idx_catalogo, sim) in enumerate(top_3_limpio):
    ax = axes[rank + 1]
    
    ruta_resultado = valid_image_paths[idx_catalogo]
    img_res = Image.open(ruta_resultado)
    
    ax.imshow(img_res)
    # Mostramos el ranking y la similitud
    ax.set_title(f"Top {rank+1} (Sim: {sim:.2f})", color='black')
    ax.axis('off')

plt.tight_layout()
plt.show()

import time
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

def demo_interactiva_produccion(ruta_imagen_usuario, top_k=3):    
    img_original = Image.open(ruta_imagen_usuario).convert('RGB')
    width, height = img_original.size
    
    # Inicia cronómetro YOLO
    t0 = time.time()
    resultados = yolo_model(img_original, conf=0.15, verbose=False)
    cajas_ropa = [box for box in resultados[0].boxes if int(box.cls[0]) == 0]

    if len(cajas_ropa) == 0:
        print("⚠️ No se detectaron prendas claras. Aplicando protocolo Fallback (Imagen completa)...")
        img_recortada = img_original
        id_prenda = "N/A (Original)"
        tiempo_yolo = (time.time() - t0) * 1000        
    else:
        fig_menu, ax_menu = plt.subplots(figsize=(6, 6))
        ax_menu.imshow(img_original)
        ax_menu.set_title("OUTFIT DETECTADO\nMira los IDs y elige abajo", color='blue', fontweight='bold')
        ax_menu.axis('off')
        
        colores = ['red', 'cyan', 'lime', 'magenta', 'yellow']
        for i, box in enumerate(cajas_ropa):
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            color = colores[i % len(colores)]
            rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, linewidth=3, edgecolor=color, facecolor='none')
            ax_menu.add_patch(rect)
            ax_menu.text(x1, y1-10, f"ID: {i}", color='black', backgroundcolor=color, fontweight='bold')
            
        plt.show() 
        
        # Interacción por teclado
        seleccion_texto = input(f"👉 Introduce el ID de la prenda a buscar (del 0 al {len(cajas_ropa)-1}): ")
        
        try:
            id_prenda = int(seleccion_texto)
        except ValueError:
            print("No se introdujo un número, continuaremos con la prenda por defecto")
            id_prenda = 0
            
        if id_prenda < 0 or id_prenda >= len(cajas_ropa):
            print("El id introducido no existe, continuaremos con la prenda por defecto")
            id_prenda = 0            
        
        # Recorte de la opción elegida
        box_elegida = cajas_ropa[id_prenda]
        x1, y1, x2, y2 = box_elegida.xyxy[0].cpu().numpy()
        
        pad_x = (x2 - x1) * 0.05
        pad_y = (y2 - y1) * 0.05
        x1_p, y1_p = max(0, x1 - pad_x), max(0, y1 - pad_y)
        x2_p, y2_p = min(width, x2 + pad_x), min(height, y2 + pad_y)
        
        img_recortada = img_original.crop((x1_p, y1_p, x2_p, y2_p))
        tiempo_yolo = (time.time() - t0) * 1000
        
    # FASE 2: Vectorización (FashionCLIP)
    temp_path = "temp_query.jpg"
    img_recortada.save(temp_path)
    
    t1 = time.time()
    vector_usuario = get_clip_embedding(temp_path)
    tiempo_clip = (time.time() - t1) * 1000

    # FASE 3: Búsqueda a Escala (FAISS)    
    t2 = time.time()
    vector_faiss = np.array([vector_usuario]).astype('float32')
    faiss.normalize_L2(vector_faiss)
    
    distancias, indices = indice_faiss.search(vector_faiss, top_k + 1)
    tiempo_faiss = (time.time() - t2) * 1000
    
    tiempo_total = tiempo_yolo + tiempo_clip + tiempo_faiss
    
    # Log de rendimiento    
    print("-" * 50)
    print(f"⏱️ TIEMPOS DE RESPUESTA (SLA < 2000ms):")
    print(f"   -> YOLO (Recorte):        {tiempo_yolo:.2f} ms")
    print(f"   -> FashionCLIP (Vector):  {tiempo_clip:.2f} ms")
    print(f"   -> FAISS (Búsqueda):      {tiempo_faiss:.2f} ms")
    print(f"   -> TIEMPO TOTAL:          {tiempo_total:.2f} ms")
    print("-" * 50)
    
    resultados_limpios = []
    for idx, sim in zip(indices[0], distancias[0]):        
        if valid_image_paths[idx] != ruta_imagen_usuario:
            resultados_limpios.append((idx, sim))
        if len(resultados_limpios) == top_k:
            break
            
    # Visualización
    fig_res, axes = plt.subplots(1, top_k + 2, figsize=(18, 5))
    fig_res.suptitle(f"PIPELINE COMPLETADO (Búsqueda ID: {id_prenda})", fontsize=16, fontweight='bold', y=1.05)
    
    axes[0].imshow(img_original)
    axes[0].set_title("1. INPUT DEL USUARIO\n(Street Photo)", color='blue')
    axes[0].axis('off')
    
    axes[1].imshow(img_recortada)
    axes[1].set_title(f"2. IA / FALLBACK\n(Prenda: {id_prenda})", color='orange')
    axes[1].axis('off')
    
    for i, (idx, sim) in enumerate(resultados_limpios):
        ax = axes[i + 2]
        img_res = Image.open(valid_image_paths[idx])
        ax.imshow(img_res)
        ax.set_title(f"Recomendación {i+1}\nSimilitud: {sim:.2f}", color='green')
        ax.axis('off')
        
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

# Demo
imagen_de_prueba = valid_image_paths[24]  
demo_interactiva_produccion(imagen_de_prueba, top_k=3)