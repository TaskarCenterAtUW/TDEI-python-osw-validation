import uuid
import logging
import datetime
import urllib.parse
from typing import List
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from python_ms_core.core.auth.models.permission_request import PermissionRequest
from .validation import Validation
from .models.queue_message_content import Upload, ValidationResult
from .config import Settings
import threading

logging.basicConfig()
logger = logging.getLogger('OSW_VALIDATOR')
logger.setLevel(logging.INFO)


class OSWValidator:
    _settings = Settings()

    def __init__(self):
        core = Core()
        options = {
            'provider': self._settings.auth_provider,
            'api_url': self._settings.auth_permission_url
        }
        listening_topic_name = self._settings.event_bus.upload_topic or ''
        publishing_topic_name = self._settings.event_bus.validation_topic or ''
        self.subscription_name = self._settings.event_bus.upload_subscription or ''
        self.listening_topic = core.get_topic(topic_name=listening_topic_name)
        self.publishing_topic = core.get_topic(topic_name=publishing_topic_name)
        self.logger = core.get_logger()
        self.storage_client = core.get_storage_client()
        self.auth = core.get_authorizer(config=options)
        self.container_name = self._settings.event_bus.container_name
        self.start_listening()

    def start_listening(self):
        def process(message) -> None:
            if message is not None:
                queue_message = QueueMessage.to_dict(message)
                upload_message = Upload.data_from(queue_message)
                process_thread = threading.Thread(target=self.validate, args=[upload_message])
                process_thread.start()
                # self.validate(upload_message)

        self.listening_topic.subscribe(subscription=self.subscription_name, callback=process)

    def validate(self, received_message: Upload):
        tdei_record_id: str = ''
        try:
            tdei_record_id = received_message.message_id
            logger.info(f'Received message for : {tdei_record_id} Message received for OSW validation !')

            if received_message.data.file_upload_path is None:
                error_msg = 'Request does not have valid file path specified.'
                logger.error(f'{tdei_record_id}, {error_msg} !')
                raise Exception(error_msg)

            if 'VALIDATION_ONLY' not in received_message.message_type:
                if self.has_permission(roles=['tdei-admin', 'poc', 'osw_data_generator'],
                                       queue_message=received_message) is None:
                    error_msg = 'Unauthorized request !'
                    logger.error(tdei_record_id, error_msg, received_message)
                    raise Exception(error_msg)

            file_upload_path = urllib.parse.unquote(received_message.data.file_upload_path)
            if file_upload_path:
                validation_result = Validation(file_path=file_upload_path, storage_client=self.storage_client)
                result = validation_result.validate()
                self.send_status(result=result, upload_message=received_message)
            else:
                raise Exception('File entity not found')
        except Exception as e:
            logger.error(f'{tdei_record_id} Error occurred while validating OSW request, {e}')
            result = ValidationResult()
            result.is_valid = False
            result.validation_message = f'Error occurred while validating OSW request {e}'
            self.send_status(result=result, upload_message=received_message)

    def send_status(self, result: ValidationResult, upload_message: Upload):
        upload_message.data.success = result.is_valid
        upload_message.data.message = result.validation_message

        data = QueueMessage.data_from({
            'messageId': upload_message.message_id,
            'messageType': upload_message.message_type,
            'data': upload_message.data.to_json()
        })
        try:
            self.publishing_topic.publish(data=data)
        except Exception as e:
            print(e)
        logger.info(f'Publishing message for : {upload_message.message_id}')

    def has_permission(self, roles: List[str], queue_message: Upload) -> bool:
        try:
            permission_request = PermissionRequest(
                user_id=queue_message.data.user_id,
                project_group_id=queue_message.data.tdei_project_group_id,
                permissions=roles,
                should_satisfy_all=False
            )
            response = self.auth.has_permission(request_params=permission_request)
            return response if response is not None else False
        except Exception as error:
            print('Error validating the request authorization:', error)
            return False
