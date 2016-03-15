import pika

from supporting.mq_constants import MQConstants


class DataSender():
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=MQConstants.localhost))
        channel = connection.channel()

        channel.exchange_declare(exchange=MQConstants.data_back_flow,
                                 type=MQConstants.fanout)

        message = "info: Hello World!"
        channel.basic_publish(exchange=MQConstants.data_back_flow,
                              routing_key='',
                              body=message)
        print(" [x] Sent %r" % message)
        connection.close()

if __name__ == '__main__':
    sender = DataSender()