import json
import random

import pika
import sys

from rmq.base.work_agent import WorkAgent
from supporting.mq_constants import MQConstants, Message, Level, Task
from supporting.primitives import pack_msg_json
from supporting.ttuple_exceptions import UnexpectedMessageError
from two_tuple.base.linguistic_set import LinguisticSet
from two_tuple.base.two_tuple import TwoTuple


class Expert(WorkAgent):
    NUM_SETS = 6

    def __init__(self, name):
        self._estimates = None
        self.name = name
        self._alternatives = []
        self.options = []
        self._personal_best = -1
        self._community_best = -1
        self._linguistic_set = []
        self.PROBABLE_AGENTSET_SIZE = 5  # it means nothing, just to get the seed for generating random number

        # now connect and begin listening
        super().__init__()

    def set_linguistic_set(self):
        l = []
        size = 3
        for i in range(Expert.NUM_SETS):
            l.append( LinguisticSet(["_".join(["good", str(size), str(j)]) for j in range(size)]))
            size = size * 2 - 1
        self.linguistic_set = random.choice(l)

    @property
    def linguistic_set(self):
        return self._linguistic_set

    @linguistic_set.setter
    def linguistic_set(self, value):
        self._linguistic_set = value

    @property
    def alternatives(self):
        return self._alternatives

    @alternatives.setter
    def alternatives(self, value):
        self._alternatives = value

    @property
    def estimates(self):
        return self._estimates

    @estimates.setter
    def estimates(self, value):
        self._estimates = value

    def calculate_estimates(self):
        assert self._alternatives, "Alternatives should not be empty"
        self.estimates = [random.choice(self.linguistic_set.options) for j in range(len(self.alternatives))]

    def get_estimates(self):
        return self.estimates

    def set_estimate_options(self, options):
        assert options, "Options should not be empty"
        self.options = options

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
            # if not command:
            data = {}
            if (body):
                data = json.loads(body)
                print("My special task: " + str(data))
            if len(command) > 0:
                if command[1] == Task.set_options:
                    print("Got options and experts participating. Saved them")
                    try:
                        options_from_center = data["alternatives"]
                    except KeyError:
                        raise UnexpectedMessageError("Expected to get alternatives")
                    else:
                        self.alternatives = options_from_center

                        # finally decide what is the scale for our estimates
                        self.set_linguistic_set()

                        message = pack_msg_json(level=Level.info, body={"info": Task.set_options})
                        self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
                elif command[1] == Task.get_estimates:
                    print("Preparing and sending my estimates and the whole scale")
                    self.calculate_estimates()
                    message = pack_msg_json(level=Level.info,
                                            body={Message.info: Task.get_estimates,
                                                  "data": self.estimates,
                                                  "linguistic_set_size": self.linguistic_set.size})
                    self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
                elif command[1] == Task.set_community_best:
                    print("Got community best")
                    try:
                        best_from_server = TwoTuple.from_json(data[Message.best_alternative])
                        best_from_server_id = data[Message.best_alternative_id]
                    except KeyError:
                        raise UnexpectedMessageError("Expected to get best alternative")
                    else:

                        tuple_estimates = [TwoTuple.from_string(i) for i in self.estimates]
                        personal_best = tuple_estimates[best_from_server_id]
                        if personal_best < best_from_server:
                            satisfaction = "not_satisfied"
                        elif personal_best == best_from_server:
                            satisfaction = "satisfied"
                        else:
                            satisfaction = "over_satisfied"
                        message = pack_msg_json(level=Level.info,
                                                body={Message.info: Task.set_community_best, Message.satisfaction: satisfaction})
                        self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
                elif command[1] == Task.finish_game:
                    print("I leave the room")
                    message = pack_msg_json(level=Level.info, body={"info": Task.finish_game})
                    self.send_message(message=message, routing_key=self.make_routing_key(" ", "info"))
                    sys.exit(0)
            else:
                print("I got some unknown task.")

        except ValueError:
            if Message.kill_everyone in body:
                print("Bye!")
                sys.exit(-1)
        except UnexpectedMessageError as e:
            print("Need to notify the central that there is something wrong with him. " + e.message)


if __name__ == '__main__':
    print('Starting to initialize the expert')
    e = Expert("expert1")
    # options = ["good", "bad", "excellent", "satisfactory"]
    # e.set_estimate_options(options)
    # alt = [chr(i) for i in range(4)]
    # e.set_alternatives(alt)
    # e.calculate_estimates()
    # print(e.get_estimates())
