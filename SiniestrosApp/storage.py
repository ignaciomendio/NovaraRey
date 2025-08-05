# storage.py
import os
import io
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from django.utils.deconstruct import deconstructible


@deconstructible
class GoogleDriveStorage(Storage):
    """
    Custom storage backend para Google Drive
    """
    
    def __init__(self, folder_id=None):
        self.folder_id = folder_id or getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID_SINIESTOS', None)
        self._service = None
    
    @property
    def service(self):
        if self._service is None:
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_DRIVE_CREDENTIALS_FILE,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self._service = build('drive', 'v3', credentials=credentials)
        return self._service
    
    def _open(self, name, mode='rb'):
        """Abre un archivo desde Google Drive"""
        file_id = self._get_file_id(name)
        if not file_id:
            raise FileNotFoundError(f"File {name} not found in Google Drive")
        
        request = self.service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        return ContentFile(file_content.read(), name=name)
    
    def _save(self, name, content):
        """Guarda un archivo en Google Drive"""
        # Leer el contenido del archivo
        content.seek(0)
        media = MediaIoBaseUpload(
            content, 
            mimetype=self._get_mimetype(name),
            resumable=True
        )
        
        # Metadatos del archivo
        file_metadata = {
            'name': name,
            'parents': [self.folder_id] if self.folder_id else []
        }
        
        # Subir archivo
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return name
    
    def delete(self, name):
        """Elimina un archivo de Google Drive"""
        file_id = self._get_file_id(name)
        if file_id:
            self.service.files().delete(fileId=file_id).execute()
    
    def exists(self, name):
        """Verifica si un archivo existe en Google Drive"""
        return self._get_file_id(name) is not None
    
    def url(self, name): #type: ignore
        """Retorna URL pública del archivo (requiere permisos públicos)"""
        file_id = self._get_file_id(name)
        if file_id:
            return f"https://drive.google.com/file/d/{file_id}/view"
        return None
    
    def size(self, name):
        """Retorna el tamaño del archivo"""
        file_id = self._get_file_id(name)
        if file_id:
            file_info = self.service.files().get(
                fileId=file_id, 
                fields='size'
            ).execute()
            return int(file_info.get('size', 0))
        return 0
    
    def _get_file_id(self, name):
        """Busca el ID del archivo por nombre"""
        query = f"name='{name}'"
        if self.folder_id:
            query += f" and '{self.folder_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        return files[0]['id'] if files else None
    
    def _get_mimetype(self, name):
        """Determina el tipo MIME basado en la extensión"""
        import mimetypes
        mimetype, _ = mimetypes.guess_type(name)
        return mimetype or 'application/octet-stream'