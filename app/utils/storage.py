"""Azure Blob Storage utility for photo uploads.

This module handles photo storage in Azure Blob Storage for production,
with fallback to local filesystem for development.

For private containers, SAS tokens are used to generate accessible URLs.
"""
import os
import uuid
from io import BytesIO
from flask import current_app
from datetime import datetime, timedelta


def get_blob_service_client():
    """Get Azure Blob Service Client if configured."""
    connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connection_string:
        return None
    
    try:
        from azure.storage.blob import BlobServiceClient
        return BlobServiceClient.from_connection_string(connection_string)
    except ImportError:
        current_app.logger.warning("azure-storage-blob not installed")
        return None
    except Exception as e:
        current_app.logger.error(f"Failed to connect to Azure Blob Storage: {e}")
        return None


def generate_sas_url(blob_name, container_name=None, expiry_hours=8760):
    """Generate a SAS URL for a blob (default 1 year expiry for photos).
    
    Args:
        blob_name: Name of the blob
        container_name: Container name (defaults to config)
        expiry_hours: Hours until SAS token expires (default 1 year)
        
    Returns:
        str: SAS URL or None if failed
    """
    connection_string = current_app.config.get('AZURE_STORAGE_CONNECTION_STRING')
    if not connection_string:
        return None
    
    container_name = container_name or current_app.config.get('AZURE_STORAGE_CONTAINER', 'photos')
    
    try:
        from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
        
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        account_name = blob_service.account_name
        
        # Extract account key from connection string
        account_key = None
        for part in connection_string.split(';'):
            if part.startswith('AccountKey='):
                account_key = part.replace('AccountKey=', '')
                break
        
        if not account_key:
            current_app.logger.error("Could not extract account key from connection string")
            return None
        
        # Generate SAS token with read permission
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        
    except Exception as e:
        current_app.logger.error(f"Failed to generate SAS URL: {e}")
        return None


def upload_photo_to_storage(file_data, filename, content_type='image/jpeg'):
    """Upload a photo to Azure Blob Storage or local filesystem.
    
    Args:
        file_data: File bytes or file-like object
        filename: Desired filename
        content_type: MIME type of the file
        
    Returns:
        tuple: (url, storage_type) where storage_type is 'azure' or 'local'
    """
    blob_client = get_blob_service_client()
    container_name = current_app.config.get('AZURE_STORAGE_CONTAINER', 'photos')
    
    # Ensure file_data is bytes
    if hasattr(file_data, 'read'):
        file_bytes = file_data.read()
        file_data.seek(0)  # Reset for potential reuse
    else:
        file_bytes = file_data
    
    if blob_client:
        try:
            # Upload to Azure Blob Storage
            container_client = blob_client.get_container_client(container_name)
            
            # Create container if it doesn't exist
            try:
                container_client.create_container()
            except Exception:
                pass  # Container already exists
            
            blob_client_upload = container_client.get_blob_client(filename)
            
            from azure.storage.blob import ContentSettings
            blob_client_upload.upload_blob(
                file_bytes,
                content_settings=ContentSettings(content_type=content_type),
                overwrite=True
            )
            
            # Generate SAS URL for private container access
            sas_url = generate_sas_url(filename, container_name)
            
            if sas_url:
                url = sas_url
                current_app.logger.info(f"Uploaded photo to Azure Blob with SAS: {filename}")
            else:
                # Fallback to public URL (works if container has public access)
                account_name = blob_client.account_name
                url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}"
                current_app.logger.info(f"Uploaded photo to Azure Blob (public URL): {filename}")
            
            return url, 'azure'
            
        except Exception as e:
            current_app.logger.error(f"Azure upload failed, falling back to local: {e}")
    
    # Fallback to local filesystem
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    with open(file_path, 'wb') as f:
        f.write(file_bytes)
    
    url = f'/static/uploads/{filename}'
    current_app.logger.info(f"Uploaded photo to local filesystem: {filename}")
    return url, 'local'


def delete_photo_from_storage(url_or_filename):
    """Delete a photo from Azure Blob Storage or local filesystem.
    
    Args:
        url_or_filename: Full URL or just filename
    """
    # Extract filename from URL
    if url_or_filename.startswith('http'):
        # Azure URL: https://account.blob.core.windows.net/container/filename
        filename = url_or_filename.split('/')[-1]
    elif url_or_filename.startswith('/static/uploads/'):
        # Local URL: /static/uploads/filename
        filename = url_or_filename.replace('/static/uploads/', '')
    else:
        filename = url_or_filename
    
    blob_client = get_blob_service_client()
    container_name = current_app.config.get('AZURE_STORAGE_CONTAINER', 'photos')
    
    if blob_client:
        try:
            container_client = blob_client.get_container_client(container_name)
            blob_client_delete = container_client.get_blob_client(filename)
            blob_client_delete.delete_blob()
            current_app.logger.info(f"Deleted photo from Azure Blob: {filename}")
            return True
        except Exception as e:
            current_app.logger.warning(f"Azure delete failed: {e}")
    
    # Try local filesystem
    try:
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            current_app.logger.info(f"Deleted photo from local filesystem: {filename}")
            return True
    except Exception as e:
        current_app.logger.warning(f"Local delete failed: {e}")
    
    return False


def get_storage_type():
    """Check which storage backend is active.
    
    Returns:
        str: 'azure' if Azure Blob is configured, 'local' otherwise
    """
    blob_client = get_blob_service_client()
    return 'azure' if blob_client else 'local'


def generate_unique_filename(original_filename, prefix=''):
    """Generate a unique filename for storage.
    
    Args:
        original_filename: Original uploaded filename
        prefix: Optional prefix (e.g., 'thumb_')
        
    Returns:
        str: Unique filename with .jpg extension
    """
    return f"{prefix}{uuid.uuid4().hex}.jpg"

