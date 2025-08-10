from fastapi import HTTPException, status
from fastapi import UploadFile
import os

class FileValidator:
    """Utility class for file validation"""
    
    ALLOWED_EXTENSIONS = {
        'cv': ['.pdf', '.doc', '.docx'],
        'matrix': ['.xlsx', '.xls', '.csv', '.pdf']
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def validate_file_size(cls, file: UploadFile) -> None:
        """Validate file size"""
        if file.size and file.size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    @classmethod
    def validate_file_extension(cls, file: UploadFile, file_type: str) -> None:
        """Validate file extension"""
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_type in cls.ALLOWED_EXTENSIONS:
                if file_ext not in cls.ALLOWED_EXTENSIONS[file_type]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid file type. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS[file_type])}"
                    )
    
    @classmethod
    def validate_cv_file(cls, file: UploadFile) -> None:
        """Validate CV file"""
        cls.validate_file_size(file)
        cls.validate_file_extension(file, 'cv')
    
    @classmethod
    def validate_matrix_file(cls, file: UploadFile) -> None:
        """Validate competency matrix file"""
        cls.validate_file_size(file)
        cls.validate_file_extension(file, 'matrix')
