import os
import uuid
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

logger = logging.getLogger(__name__)

# Config
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "photos")

def get_blob_service_client():
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def upload_image(file_bytes: bytes, original_filename: str) -> str:
    """
    Uploads an image to Azure Blob Storage and returns the public URL.
    Generates a unique name using UUID.
    """
    ext = original_filename.split(".")[-1] if "." in original_filename else "jpg"
    unique_name = f"uploaded_{uuid.uuid4()}.{ext}"
    
    logger.info(f"Uploading image to Azure: {unique_name}")
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    blob_client = container_client.get_blob_client(unique_name)
    
    # Upload
    # Determine content_type based on ext
    content_type = "image/jpeg"
    if ext.lower() in ["png"]:
        content_type = "image/png"
        
    # We must construct ContentSettings
    my_content_settings = ContentSettings(content_type=content_type)
        
    blob_client.upload_blob(file_bytes, overwrite=True, content_settings=my_content_settings)
    
    return blob_client.url
