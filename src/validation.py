import os
import shutil
import logging
import traceback
from pathlib import Path
from .config import Settings
from python_osw_validation import OSWValidation
from .models.queue_message_content import ValidationResult

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path used for download file generation.
DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'

logging.basicConfig()
logger = logging.getLogger('OSW_VALIDATION')
logger.setLevel(logging.INFO)


class Validation:
    def __init__(self, file_path=None, storage_client=None):
        settings = Settings()
        self.container_name = settings.event_bus.container_name
        self.storage_client = storage_client
        self.file_path = file_path
        self.file_relative_path = file_path.split('/')[-1]
        self.client = self.storage_client.get_container(container_name=self.container_name)

    def validate(self) -> ValidationResult:
        return self.is_osw_valid()

    def is_osw_valid(self) -> ValidationResult:
        result = ValidationResult()
        result.is_valid = False
        result.validation_message = ''
        root, ext = os.path.splitext(self.file_relative_path)
        if ext and ext.lower() == '.zip':
            downloaded_file_path = self.download_single_file(self.file_path)
            logger.info(f' Downloaded file path: {downloaded_file_path}')
            validator = OSWValidation(zipfile_path=downloaded_file_path)
            validation_result = validator.validate()
            result.is_valid = validation_result.is_valid
            if not result.is_valid:
                result.validation_message = validation_result.errors
                # logger.error(f' Error While Validating File: {str(validation_result.errors)}')
            Validation.clean_up(downloaded_file_path)
        else:
            result.validation_message = 'Failed to validate because unknown file format'
            logger.error(f' Failed to validate because unknown file format')

        return result

    def download_single_file(self, file_upload_path=None) -> str:
        is_exists = os.path.exists(DOWNLOAD_FILE_PATH)
        if not is_exists:
            os.makedirs(DOWNLOAD_FILE_PATH)

        file = self.storage_client.get_file_from_url(self.container_name, file_upload_path)
        try:
            if file.file_path:
                file_path = os.path.basename(file.file_path)
                with open(f'{DOWNLOAD_FILE_PATH}/{file_path}', 'wb') as blob:
                    blob.write(file.get_stream())
                logger.info(f' File downloaded to location: {DOWNLOAD_FILE_PATH}/{file_path}')
                return f'{DOWNLOAD_FILE_PATH}/{file_path}'
            else:
                logger.info(' File not found!')
        except Exception as e:
            traceback.print_exc()
            logger.error(e)

    @staticmethod
    def clean_up(path):
        if os.path.isfile(path):
            logger.info(f' Removing File: {path}')
            os.remove(path)
        else:
            folder = os.path.join(DOWNLOAD_FILE_PATH, path)
            logger.info(f' Removing Folder: {folder}')
            shutil.rmtree(folder, ignore_errors=False)
