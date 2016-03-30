import json
import sys

import pika

from supporting.mq_constants import MQConstants, Message, Level
from supporting.primitives import pack_msg_json


class DataSender():
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel = self.connection.channel()
        self.result = self.channel.queue_declare(exclusive=True, durable=True)
        self.queue_name = self.result.method.queue
        self.routing_key = "routing_key"  # '.'.join([str(self.ID), "report", "update_energy"])

        try:
            self.ID
        except AttributeError:
            data = {Message.new_member: ""}
            self.send_message(message=data, routing_key=Message.new_member)
        else:
            self.ID = int(1)
            data = {}
            data[Message.info] = "I am now enumerated. So, check the connection with my routing_key"
            message = pack_msg_json(level=Level.info, body=data)
            self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))

        self.begin_listen(queue_name=self.queue_name)

    def send_message(self, message, routing_key):
        """
        Standard Rabbit MQ interface for sending the message
        :param message:
        :param routing_key:
        """
        print("[*] Sending Task: " + str(message))

        try:
            message[Message.info] = "[{}] {}".format(str(self.ID), message[Message.info])
        except (ValueError, AttributeError,TypeError):
            pass
        message = json.dumps(message)
        self.channel.exchange_declare(exchange=MQConstants.directExchangeToAdmin,
                                      type='topic')
        self.channel.basic_publish(exchange=MQConstants.directExchangeToAdmin,
                                   routing_key=routing_key,
                                   properties=pika.BasicProperties(type="task", delivery_mode=1),
                                   body=message)

    def begin_listen(self, queue_name, route_key=None):
        """
        Makes this instance (agent) listen to the messages from the broker
        :param queue_name:
        """
        self.channel.exchange_declare(exchange=MQConstants.fanoutExchangeFromAdmin,
                                      type='fanout')
        if route_key:
            route_key = "{}.*.*".format(route_key)
        else:
            route_key = MQConstants.routing_key_from_admin
        self.channel.queue_bind(exchange=MQConstants.fanoutExchangeFromAdmin, queue=self.queue_name,
                                routing_key=route_key)
        print("[*] Waiting for messages...")

        self.channel.basic_consume(self.receive_message, queue=self.queue_name, no_ack=False)

        self.channel.start_consuming()

    def make_routing_key(self, type, level="report"):
        return '.'.join([str(self.ID), level, type])

    def receive_message(self, ch, method, properties, body):

        """
        Standard interface for the pika module for the agent to get messages
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        body = body.decode("utf-8")
        if "admin" in body:
            print("Hey, Admin!")

        try:
            data = json.loads(body)
            if (data.get(Message.new_id, -1) > -1):
                self.ID = data.get(Message.new_id, 0)
                print("Wow, new id: " + str(self.ID))
                self.channel.stop_consuming()
                self.change_routing_key()
            print("In receiving info " + str(data))
        except ValueError:
            if Message.new_id in body:
                if self.ID == -1:
                    self.ID = body.split()[-1]
                    print("My ID: " + str(self.ID))
                    message = pack_msg_json(level=Level.info)
                    self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
                return
            elif Message.kill_everyone in body:
                print("Bye!")
                sys.exit(0)

    def receive_topic_messages(self, ch, method, properties, body):
        """
        Standard interface for the pika module for the agent to get messages
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        body = body.decode("utf-8")
        if "admin" in body:
            print("Hey, Admin!")

        try:
            command = method.routing_key.split('.')
            if not command:
                data = json.loads(body)
                print("My special task: " + str(data))
            elif len(command):
                if command[1] == "get_scales":
                    print("Preparing and sending my scales")
                    message = pack_msg_json(level=Level.info,body={"scale":['A','B','C']})
                    self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
            elif command[1] == "get_estimates":
                    print("Preparing and sending my estimates")

        except ValueError:
            if Message.kill_everyone in body:
                print("Bye!")
                sys.exit(-1)

    def change_routing_key(self):
        self.channel.stop_consuming()
        self.connection2 = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.channel2 = self.connection2.channel()
        self.result2 = self.channel2.queue_declare(exclusive=True, durable=True)
        self.queue_name2 = self.result2.method.queue
        self.channel2.exchange_declare(exchange=MQConstants.topicExchangeFromAdmin,
                                       type='topic')

        if self.ID >= 0:
            self.routing_key = "{}.*".format(self.ID)
        else:
            self.routing_key = MQConstants.routing_key_from_admin
        self.channel2.queue_bind(exchange=MQConstants.topicExchangeFromAdmin, queue=self.queue_name2,
                                 routing_key=self.routing_key)
        print("[*] Waiting for messages...")

        self.channel2.basic_consume(self.receive_topic_messages, queue=self.queue_name2, no_ack=False)

        self.channel2.start_consuming()


if __name__ == '__main__':
    sender = DataSender()
