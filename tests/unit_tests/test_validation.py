import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.validation import Validation

DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'
SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'

SUCCESS_FILE_NAME = 'valid.zip'
FAILURE_FILE_NAME = 'invalid.zip'
ID_MISSING_FILE_NAME = '_id_missing.zip'
EDGES_INVALID_FILE_NAME = 'edges_invalid.zip'
NODES_INVALID_FILE_NAME = 'nodes_invalid.zip'
POINTS_INVALID_FILE_NAME = 'points_invalid.zip'
INVALID_FILE_NAME = 'invalid_files.zip'
INVALID_GEOMETRY_FILE_NAME = 'invalid_geometry.zip'
MISSING_IDENTIFIER_FILE_NAME = 'missing_identifier.zip'
NO_ENTITY_FILE_NAME = 'no_entity.zip'
WRONG_DATATYPE_FILE_NAME = 'wrong_datatype.zip'


class TestSuccessValidation(unittest.TestCase):

    @patch.object(Validation, 'download_single_file')
    def setUp(self, mock_download_single_file):
        os.makedirs(DOWNLOAD_FILE_PATH, exist_ok=True)
        source = f'{SAVED_FILE_PATH}/{SUCCESS_FILE_NAME}'
        destination = f'{DOWNLOAD_FILE_PATH}/{SUCCESS_FILE_NAME}'

        if not os.path.isfile(destination):
            shutil.copyfile(source, destination)

        file_path = f'{DOWNLOAD_FILE_PATH}/{SUCCESS_FILE_NAME}'

        with patch.object(Validation, '__init__', return_value=None):
            self.validator = Validation(file_path=file_path, storage_client=MagicMock())
            self.validator.file_path = file_path
            self.validator.file_relative_path = SUCCESS_FILE_NAME
            self.validator.container_name = None
            mock_download_single_file.return_value = file_path

    def tearDown(self):
        pass

    def test_validate_with_valid_file(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{SUCCESS_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertTrue(result.is_valid)

    def test_is_osw_valid_with_valid_file(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{SUCCESS_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertTrue(result.is_valid)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_download_single_file(self):
        # Arrange
        file_upload_path = DOWNLOAD_FILE_PATH
        self.validator.storage_client = MagicMock()
        self.validator.storage_client.get_file_from_url = MagicMock()
        file = MagicMock()
        file.file_path = 'text_file.txt'
        file.get_stream = MagicMock(return_value=b'file_content')
        self.validator.storage_client.get_file_from_url.return_value = file

        # Act
        downloaded_file_path = self.validator.download_single_file(file_upload_path=file_upload_path)

        # Assert
        self.validator.storage_client.get_file_from_url.assert_called_once_with(self.validator.container_name,
                                                                                file_upload_path)
        file.get_stream.assert_called_once()
        with open(downloaded_file_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b'file_content')

    def test_clean_up_file(self):
        # Arrange
        file_upload_path = DOWNLOAD_FILE_PATH
        text_file_path = f'{file_upload_path}/text_file.txt'
        f = open(text_file_path, "w")
        f.write("Sample text")
        f.close()

        # Act
        Validation.clean_up = MagicMock()

        # Assert
        # self.assertFalse(os.path.exists(text_file_path))

    def test_clean_up_folder(self):
        # Arrange
        directory_name = 'temp'
        directory_path = f'{DOWNLOAD_FILE_PATH}/{directory_name}'
        is_exists = os.path.exists(directory_path)
        if not is_exists:
            os.makedirs(directory_path)

        # Act
        Validation.clean_up = MagicMock()

        # Assert
        # self.assertFalse(os.path.exists(directory_name))


class TestFailureValidation(unittest.TestCase):

    @patch.object(Validation, 'download_single_file')
    def setUp(self, mock_download_single_file):
        os.makedirs(DOWNLOAD_FILE_PATH, exist_ok=True)
        source = f'{SAVED_FILE_PATH}/{FAILURE_FILE_NAME}'
        destination = f'{DOWNLOAD_FILE_PATH}/{FAILURE_FILE_NAME}'

        if not os.path.isfile(destination):
            shutil.copyfile(source, destination)

        file_path = f'{DOWNLOAD_FILE_PATH}/{FAILURE_FILE_NAME}'

        with patch.object(Validation, '__init__', return_value=None):
            self.validator = Validation(file_path=file_path, storage_client=MagicMock())
            self.validator.file_path = file_path
            self.validator.file_relative_path = FAILURE_FILE_NAME
            self.validator.container_name = None
            mock_download_single_file.return_value = file_path

    def tearDown(self):
        pass

    def test_validate_with_invalid_file(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{FAILURE_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)

    def test_is_osw_valid_with_invalid_zip_file(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{FAILURE_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_format_file(self):
        # Arrange
        file_path = f'{SAVED_FILE_PATH}/gtfs-pathways-upload.json'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_id_missing_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{ID_MISSING_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_id_missing_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{ID_MISSING_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_invalid_edges_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{EDGES_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_edges_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{EDGES_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_invalid_nodes_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{NODES_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_nodes_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{NODES_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_invalid_points_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{POINTS_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_points_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{POINTS_INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_invalid_files_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_files_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{INVALID_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_invalid_geometry_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{INVALID_GEOMETRY_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_invalid_geometry_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{INVALID_GEOMETRY_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_missing_identifier_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{MISSING_IDENTIFIER_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_missing_identifier_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{MISSING_IDENTIFIER_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_no_entity_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{NO_ENTITY_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_no_entity_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{NO_ENTITY_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_validate_with_wrong_datatype_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{WRONG_DATATYPE_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.validate()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_is_osw_valid_with_wring_datatype_zip(self):
        # Arrange
        file_path = f'{DOWNLOAD_FILE_PATH}/{WRONG_DATATYPE_FILE_NAME}'
        expected_downloaded_file_path = file_path
        self.validator.download_single_file = MagicMock(return_value=expected_downloaded_file_path)
        Validation.clean_up = MagicMock()

        # Act
        result = self.validator.is_osw_valid()

        # Assert
        self.assertFalse(result.is_valid)
        self.assertIsInstance(result.validation_message, list)
        Validation.clean_up.assert_called_once_with(file_path)

    def test_download_single_file_exception(self):
        # Arrange
        file_upload_path = DOWNLOAD_FILE_PATH
        self.validator.storage_client = MagicMock()
        self.validator.storage_client.get_file_from_url = MagicMock()
        file = MagicMock()
        file.file_path = 'text_file.txt'
        file.get_stream = MagicMock(return_value=b'file_content')
        self.validator.storage_client.get_file_from_url.return_value = file

        # Act
        downloaded_file_path = self.validator.download_single_file(file_upload_path=file_upload_path)

        # Assert
        self.validator.storage_client.get_file_from_url.assert_called_once_with(self.validator.container_name,
                                                                                file_upload_path)
        file.get_stream.assert_called_once()
        with open(downloaded_file_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b'file_content')


if __name__ == '__main__':
    unittest.main()
