import pika

from supporting.mq_constants import MQConstants


class DataReceiver:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=MQConstants.localhost))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange=MQConstants.data_back_flow,
                                 type=MQConstants.fanout)

        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange=MQConstants.data_back_flow,
                           queue=self.queue_name)

        print(' [*] Waiting for logs. To exit press CTRL+C')



        self.channel.basic_consume(self.callback,
                              queue=self.queue_name,
                              no_ack=True)

        self.channel.start_consuming()


        self.send_message(message="Hi all. I am admin.")
        self.start_listener()

    def callback(self,ch, method, properties, body):
            print(" [x] %r" % body)


if __name__ == '__main__':
    print('In data receiver!')
    receiver = DataReceiver()