import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple
import logging
from fastapi import HTTPException, UploadFile

from ..config import config

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file operations"""
    
    @staticmethod
    def validate_zip_file(file: UploadFile) -> None:
        """Validate uploaded ZIP file"""
        # Check file extension
        if not file.filename or not file.filename.lower().endswith('.zip'):
            raise HTTPException(
                status_code=400,
                detail="Only ZIP files are allowed"
            )
        
        # Check file size (this is approximate since we haven't read the full content yet)
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            current_pos = file.file.tell()
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(current_pos)  # Restore position
            
            if file_size > config.MAX_ZIP_SIZE_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {config.MAX_ZIP_SIZE_MB}MB"
                )
    
    @staticmethod
    def extract_resume_files(zip_content: bytes) -> List[Tuple[str, bytes]]:
        """
        Extract resume files from ZIP content
        Returns list of tuples: (filename, file_content)
        """
        resume_files = []
        
        try:
            # Create temporary file for ZIP content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                temp_zip.write(zip_content)
                temp_zip_path = temp_zip.name
            
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    # Get list of files in ZIP
                    file_list = zip_ref.namelist()
                    
                    for file_path in file_list:
                        # Skip directories
                        if file_path.endswith('/'):
                            continue
                        
                        # Check for directory traversal attacks
                        if '..' in file_path or file_path.startswith('/'):
                            logger.warning(f"Skipping potentially unsafe file path: {file_path}")
                            continue
                        
                        # Get file extension
                        file_ext = Path(file_path).suffix.lower()
                        
                        # Only process PDF and DOCX files
                        if file_ext in config.ALLOWED_RESUME_EXTENSIONS:
                            try:
                                file_content = zip_ref.read(file_path)
                                filename = Path(file_path).name
                                resume_files.append((filename, file_content))
                                logger.info(f"Extracted resume file: {filename}")
                            except Exception as e:
                                logger.error(f"Error reading file {file_path} from ZIP: {str(e)}")
                                continue
                        else:
                            logger.info(f"Skipping non-resume file: {file_path}")
            
            finally:
                # Clean up temporary ZIP file
                Path(temp_zip_path).unlink(missing_ok=True)
        
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted ZIP file"
            )
        except Exception as e:
            logger.error(f"Error processing ZIP file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error processing ZIP file"
            )
        
        if not resume_files:
            raise HTTPException(
                status_code=400,
                detail="No valid resume files (PDF or DOCX) found in ZIP"
            )
        
        return resume_files