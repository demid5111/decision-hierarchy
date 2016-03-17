import json

from supporting.mq_constants import Level, MQConstants


def pack_msg_json(level=Level.info, body={}):
    body[MQConstants.message_key] = level
    return json.dumps(body)
