from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESS = "file_validated_successfully"
    FILE_TYPE_NOT_SUPPORTED = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded" 
    FILE_UPLOAD_SUCCESS = "file_uploaded_successfully"
    FILE_UPLOAD_FAILED = "file_uploaded_failed"
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCESS = "processing_successfully"
    NO_FILES_FOUND = "no_files_found"
    FILE_ID_ERROR = "no_file_found_with_this_id"