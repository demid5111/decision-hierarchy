import json

from supporting.mq_constants import Level, MQConstants


def pack_msg_json(level=Level.info, body={}):
    body[MQConstants.message_key] = level
    return json.dumps(body)

def print_list(elements):
    for i in elements:
        print(i)

def print_dictionary(dic):
    for (i,j) in dic.items():
        print(str(i) + ' -> ' + str(j))