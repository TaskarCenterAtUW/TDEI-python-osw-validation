import uuid
import datetime
import urllib.parse
from typing import List
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage
from python_ms_core.core.storage.abstract.file_entity import FileEntity
from python_ms_core.core.auth.models.permission_request import PermissionRequest
from .models.queue_message_content import Upload, ValidationResult
from .config import Settings


class OswValidator:
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

    def start_listening(self):
        def process(message) -> None:
            if message is not None:
                queue_message = QueueMessage.to_dict(message)
                upload_message = Upload.data_from(queue_message)
                self.validate(upload_message)

        self.listening_topic.subscribe(subscription=self.subscription_name, callback=process)

    def validate(self, received_message: Upload):
        tdei_record_id: str = ''
        try:

            tdei_record_id = received_message.data.tdei_record_id
            print(f'Received message for : {tdei_record_id} Message received for osw validation !')
            if received_message.data.response.success is False:
                error_msg = 'Received failed workflow request'
                print(tdei_record_id, error_msg, received_message)

            if received_message.data.meta.file_upload_path is None:
                error_msg = 'Request does not have valid file path specified.'
                print(tdei_record_id, error_msg, received_message)
                raise Exception(error_msg)

            if self.has_permission(roles=['tdei-admin', 'poc', 'osw_data_generator'], queue_message=received_message) is None:
                error_msg = 'Unauthorized request !'
                print(tdei_record_id, error_msg, received_message)
                raise Exception(error_msg)

            url = urllib.parse.unquote(received_message.data.meta.file_upload_path)
            file_entity = self.storage_client.get_file_from_url(container_name=self.container_name, full_url=url)
            if file_entity:
                # TODO: Validation
                validation_result = self.dummy_validation(file_entity=file_entity, queue_message=received_message)
                self.send_status(result=validation_result, upload_message=received_message)
            else:
                raise Exception('File entity not found')
        except Exception as e:
            print(f'{tdei_record_id} Error occurred while validating osw request, {e}')
            result = ValidationResult()
            result.is_valid = False
            result.validation_message = f'Error occurred while validating osw request {e}'
            self.send_status(result=result, upload_message=received_message)

    def dummy_validation(self, file_entity: FileEntity, queue_message: Upload):
        file_name = file_entity.name
        result = ValidationResult()
        if 'invalid' in file_name:
            result.is_valid = False
            result.validation_message = 'file name contains invalid'
        else:
            result.is_valid = True
            result.validation_message = ''
        return result

    def send_status(self, result: ValidationResult, upload_message: Upload):

        upload_message.data.meta.isValid = result.is_valid
        upload_message.data.meta.validationMessage = result.validation_message
        upload_message.data.stage = 'osw-validation'

        upload_message.data.response.success = result.is_valid
        upload_message.data.response.message = result.validation_message

        data = QueueMessage.data_from({
            'messageId': uuid.uuid1().hex[0:24],
            'message': 'OSW validation output',
            'messageType': 'osw-validation',
            'data': upload_message.data.to_json(),
            'publishedDate': str(datetime.datetime.now())
        })
        self.publishing_topic.publish(data=data)
        print(f'Publishing message for : {upload_message.data.tdei_record_id}')

    def has_permission(self, roles: List[str], queue_message: Upload) -> bool:
        try:
            permission_request = PermissionRequest(
                user_id=queue_message.data.user_id,
                org_id=queue_message.data.tdei_org_id,
                permissions=roles,
                should_satisfy_all=False
            )
            response = self.auth.has_permission(request_params=permission_request)
            return response if response is not None else False
        except Exception as error:
            print('Error validating the request authorization:', error)
            return False
