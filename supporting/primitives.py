__author__ = "Demidovskij Alexander"
__copyright__ = "Copyright 2016, ML-MA-LDM Project"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "monadv@yandex.ru"
__status__ = "Development"

import json

from supporting.mq_constants import Level, MQConstants


def pack_msg_json(level=Level.info, body={}):
    """ Creates JSON string
    :param level: verbosity of message
    :param body: dictionary with contents
    :return: json string
    """
    body[MQConstants.message_key] = level
    return json.dumps(body)

def print_list(elements):
    for i in elements:
        print(i)

def print_dictionary(dic):
    for (i,j) in dic.items():
        print(str(i) + ' -> ' + str(j))