import uuid
import time
from python_ms_core import Core
from python_ms_core.core.queue.models.queue_message import QueueMessage

core = Core()

FILES_TO_UPLOAD = [
    # 'graph-10.zip',
    # 'graph-30.zip',
    # 'graph-50.zip',
    # 'graph-70.zip',
    # 'graph-90.zip',
    # 'graph-100.zip',
    # 'graph-200.zip',
    # 'graph-250.zip',
    # 'kingCounty-130.zip',
    # 'seattle.new.zip',
    # 'tacoma.zip',
    'vancouver.zip',
]


def run(publishing_topic):
    # for i in range(0, 50):
    #     messageId = str(i)
    #     message = QueueMessage.data_from({
    #         'messageId': f'{messageId}',
    #         'messageType': 'Formatter',
    #         'data': {
    #             "tdei_project_group_id": "0b41ebc5-350c-42d3-90af-3af4ad3628fb",
    #             'file_upload_path': f'https://tdeisamplestorage.blob.core.windows.net/tdei-storage-test/input/graph-10.zip',
    #             'user_id': '285f0ceb - 2816 - 451d - 8140 - 1e8ed7399993',
    #         },
    #     })
    #
    #     publishing_topic.publish(data=message)
    #     print(f'Sent message: {messageId}')
    #     time.sleep(1)

    for i in FILES_TO_UPLOAD:
        messageId = uuid.uuid1().hex[0:24]
        message = QueueMessage.data_from({
            'messageId': uuid.uuid1().hex[0:24],
            'messageType': 'Formatter',
            'data': {
                    "tdei_project_group_id": "0b41ebc5-350c-42d3-90af-3af4ad3628fb",
                    'file_upload_path': f'https://tdeisamplestorage.blob.core.windows.net/tdei-storage-test/input/{i}',
                    'user_id': '285f0ceb - 2816 - 451d - 8140 - 1e8ed7399993',
                },
        })

        publishing_topic.publish(data=message)
        print(f'Sent message: {messageId}')



topic = core.get_topic(topic_name='temp-anuj')
run(topic)
