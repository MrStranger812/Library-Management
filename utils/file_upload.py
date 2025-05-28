import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from utils.logger import get_logger

logger = get_logger('app')

class FileUpload:
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'jpg', 'jpeg', 'gif'},
        'document': {'pdf', 'doc', 'docx', 'txt'},
        'csv': {'csv'},
        'all': {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv'}
    }
    
    @staticmethod
    def allowed_file(filename, file_type='all'):
        """Check if file extension is allowed"""
        allowed_extensions = FileUpload.ALLOWED_EXTENSIONS.get(file_type, FileUpload.ALLOWED_EXTENSIONS['all'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def save_file(file, folder='uploads', file_type='all', custom_filename=None):
        """
        Save uploaded file
        
        Args:
            file: File object from request.files
            folder: Subfolder within the upload directory
            file_type: Type of file for extension validation
            custom_filename: Custom filename (optional)
        
        Returns:
            Tuple (success, filename or error message)
        """
        if file and file.filename:
            if not FileUpload.allowed_file(file.filename, file_type):
                return False, f"File type not allowed. Allowed types: {', '.join(FileUpload.ALLOWED_EXTENSIONS[file_type])}"
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'static', folder)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Generate unique filename
            if custom_filename:
                filename = secure_filename(custom_filename)
            else:
                original_filename = secure_filename(file.filename)
                extension = original_filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{extension}"
            
            file_path = os.path.join(upload_dir, filename)
            
            try:
                file.save(file_path)
                logger.info(f"File saved: {file_path}")
                return True, os.path.join(folder, filename)
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                return False, f"Error saving file: {str(e)}"
        
        return False, "No file provided"
    
    @staticmethod
    def delete_file(filename, folder='uploads'):
        """
        Delete file
        
        Args:
            filename: Filename to delete
            folder: Subfolder within the upload directory
        
        Returns:
            Boolean indicating success
        """
        if not filename:
            return False
        
        # Get just the filename without the folder path
        if '/' in filename:
            filename = filename.split('/')[-1]
        
        file_path = os.path.join(current_app.root_path, 'static', folder, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
                return False
        
        logger.warning(f"File not found for deletion: {file_path}")
        return False