__author__ = "Demidovskij Alexander"
__copyright__ = "Copyright 2016, ML-MA-LDM Project"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "monadv@yandex.ru"
__status__ = "Development"

import json
import threading

import pika

from supporting.mq_constants import MQConstants, Message, Level
from supporting.primitives import pack_msg_json


class CentralAgent:
    """ Class CentralAgent is base class for the coordinator, who manipulates other workers/agents/experts.
    It sends messages by fanout and gets direct ones
    """
    def __init__(self):
        self.CURRENT_MAX_ID = 0
        self.NUM_EXPERTS = 3
        self.readiness = []
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()

        self.result = self.channel.queue_declare(exclusive=True, durable=True)
        self.queue_name = self.result.method.queue

        data = {}
        data[Message.info] = "Hello, World! I am admin!"
        self.send_message(message=data)
        self.start_listener()

    def receive_messages(self):
        """
		Starts listening, the agent subscribes to the direct exchange
		"""
        print("[*] Waiting for messages...")

        self.channel.exchange_declare(exchange=MQConstants.directExchangeToAdmin,
                                      type='topic')
        self.channel.queue_bind(exchange=MQConstants.directExchangeToAdmin, queue=self.queue_name,
                                routing_key=MQConstants.key_all_messages)

        self.channel.basic_consume(self.receive_message, queue=self.queue_name, no_ack=True)

        self.channel.start_consuming()

    def receive_message(self, ch, method, properties, body):
        """
        Standard interface for the pika module for the agent to get messages
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        try:
            sender_id = int(method.routing_key.split('.')[0])
        except (AttributeError,ValueError):
            if not Message.new_member in method.routing_key:
                print("I expect either ID or at least request for ID")
                return

        try:
            data = json.loads(body.decode("utf-8") )
            if Message.new_member in method.routing_key:
                print("Nice to see you, new member. Your number is now: {}!".format(str(self.CURRENT_MAX_ID)))
                # self.readiness[self.CURRENT_MAX_ID] = True
                data = {Message.new_id: self.CURRENT_MAX_ID}
                self.CURRENT_MAX_ID += 1
                self.send_message(message=data)
            elif Message.info in method.routing_key:
                print("Nice to see you, Number {}!".format(sender_id))
                data = {}
                data[Message.info] = "You are now a part of the family..."
                self.send_message(message=data)

        except ValueError as e:
            print("[x] {}".format(body))

    def start_listener(self):
        """
        Creates special thread to listen to messages from other agents
        As it receives and sends messages asynchronously, it  can be performed in different thread only.
                """
        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.receiver_thread.start()
        self.receiver_thread.join(0)

    def send_message(self, message):
        """
        Standard interface for the pika module for the agent to send messages
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        self.channel.exchange_declare(exchange=MQConstants.fanoutExchangeFromAdmin,
                                      type='fanout')
        print("[*] Sending Task: " + str(message))

        try:
            message[Message.info] = '[ADMIN] ' + message[Message.info]
        except (ValueError,KeyError):
            pass

        message = json.dumps(message)
        self.channel.basic_publish(exchange=MQConstants.fanoutExchangeFromAdmin,
                                   routing_key=MQConstants.routing_key_from_admin,
                                   properties=pika.BasicProperties(type="task", delivery_mode=2),
                                   body=message)

    def is_network_ready(self):
        """
        Checks if every machine in network has completed a task
        :return:
        """
        isReady = True
        for i in self.readiness:
            if not i:
                isReady = False
                break
        return isReady

    def prepare_readiness_list(self):
        self.readiness = [False for i in range(self.NUM_EXPERTS)]

    def erase_readiness(self):
        self.readiness = [False for i in self.readiness]


if __name__ == '__main__':
    print('In data receiver!')
    receiver = CentralAgent()
    receiver.prepare_readiness_list()

    print("Wait until I get enough experts")

    while True:
        if receiver.is_network_ready():
            break

    receiver.erase_readiness()

    print("Experts were created! Ready to go!")


    for i in range(receiver.NUM_EXPERTS):
        message = json.dumps({"my_task": "new_task"})

        receiver.channel.basic_publish(exchange=MQConstants.topicExchangeFromAdmin,
                                       routing_key=str(i)+".get_scales",
                                       properties=pika.BasicProperties(type="task", delivery_mode=2),
                                       body=message)

    print("Wait until I get enough responds")

    while True:
        if receiver.is_network_ready():
            break

    receiver.erase_readiness()
