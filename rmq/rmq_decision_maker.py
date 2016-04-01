import json
import os

import pika
import sys

from rmq.base.cental_agent import CentralAgent
from supporting.mq_constants import MQConstants, Message, Task
from supporting.ttuple_exceptions import UnexpectedMessageError
from two_tuple.lh_decison_maker import LHDecisionMaker


class RMQDecisionMaker(CentralAgent):
    def __init__(self):
        super().__init__()
        self._desicion_maker = LHDecisionMaker()

    @property
    def decision_maker(self):
        return self._desicion_maker

    @decision_maker.setter
    def decision_maker(self, value):
        self._desicion_maker = value

    def wait_for_agents(self, before_message="Waiting", after_message="Ready"):
        print(before_message)

        while True:
            if self.is_network_ready():
                break

        self.erase_readiness()

        print(after_message)

        import time
        time.sleep(1)

    def broadcast_task_msg(self, task, message_dic=None):
        for i in range(self.NUM_EXPERTS):
            message = json.dumps(message_dic)

            self.channel.basic_publish(exchange=MQConstants.topicExchangeFromAdmin,
                                       routing_key="".join([str(i), ".", task]),
                                       properties=pika.BasicProperties(type="task", delivery_mode=2),
                                       body=message)
            print("I've just sent the message to agent #{}: {}".format(str(i), message))

    def receive_message(self, ch, method, properties, body):
        """
        Standard interface for the pika module for the agent to get messages
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        sender_id = -1
        try:
            sender_id = int(method.routing_key.split('.')[0])
        except (AttributeError, ValueError):
            if not Message.new_member in method.routing_key:
                print("I expect either ID or at least request for ID")
                return

        try:
            data = json.loads(body.decode("utf-8"))
            if type(data) == str:
                data = json.loads(data)
            if Message.new_member in method.routing_key:
                print("Nice to see you, new member. Your number is now: {}!".format(str(self.CURRENT_MAX_ID)))
                # self.readiness[self.CURRENT_MAX_ID] = True
                data = {Message.new_id: self.CURRENT_MAX_ID}
                self.CURRENT_MAX_ID += 1
                self.send_message(message=data)
            elif data[Message.info] == Message.approve_enumeration:
                sender_id = data["id"]
                print("You are now a part of the family, Agent #{}".format(str(sender_id)))
                self.readiness[sender_id] = True
            elif Message.info in method.routing_key:
                next_step = data[Message.info]
                if Task.set_options in next_step:
                    print("Number {} <Task:{}> done !".format(sender_id, Task.set_options))
                    self.readiness[sender_id] = True
                elif Task.get_estimates in next_step:
                    print("Number {} <Task:{}> done !".format(sender_id, Task.get_estimates))
                    try:
                        expert_estimates = data[Message.data]
                        expert_set_size = data[Message.linguistic_set_size]
                    except KeyError:
                        raise UnexpectedMessageError("Expected to get estimates and lingvo set size")
                    else:
                        self.decision_maker.expert_to_set_id[sender_id] = self.decision_maker.get_set_id_by_size(
                            expert_set_size)
                        self.decision_maker.results[sender_id] = expert_estimates
                    self.readiness[sender_id] = True
                elif Task.set_community_best in next_step:
                    print("Number {} <Task:{}> done ! He is: {}".format(sender_id, Task.set_community_best,data[Message.satisfaction]))
                    self.readiness[sender_id] = True
                elif Task.finish_game in next_step:
                    print("Number {} <Task:{}> done !".format(sender_id, Task.finish_game))
                    self.readiness[sender_id] = True
                elif Message.satisfaction in data.keys():
                    print("Number {} <Task:{}> done !".format(sender_id, Task.finish_game))
                    self.readiness[sender_id] = True
                else:
                    print("Nice to see you, Number {}!".format(sender_id))
                    self.readiness[sender_id] = True
            else:
                data = {Message.info: "You are now a part of the family..."}
                self.send_message(message=data)
        except ValueError as e:
            print("[x] {}".format(body))
        except UnexpectedMessageError as e:
            print("Catched error: {}".format(e.message))

    def start_game(self):
        self.prepare_readiness_list()

        self.wait_for_agents(before_message="Wait until I get enough experts",
                             after_message="Experts were created! Ready to go!")

        self.decision_maker.define_alternatives()

        message = {"alternatives": self.decision_maker.alternatives}
        self.broadcast_task_msg(task=Task.set_options, message_dic=message)

        self.wait_for_agents(before_message="Wait until everyone gets options",
                             after_message="Experts got options! Ready to go!")

        # first generate linguistic sets
        # TODO: make this generation more intellectual
        self.decision_maker.retrieve_sets()
        self.decision_maker.choose_best_set()

        message = {}
        self.broadcast_task_msg(task=Task.get_estimates, message_dic=message)

        self.wait_for_agents(before_message="Wait until everyone shares his estimates",
                             after_message="Experts shared estimates! Ready to go!")

        res, index, translations = self.decision_maker.lh_two_tuple_decision()

        for (expert_id, set_id) in self.decision_maker.expert_to_set_id.items():
            message_dic = {Message.info: Task.set_community_best,
                           Message.best_alternative: translations[set_id].to_json(),
                           Message.best_alternative_id: index}
            message = json.dumps(message_dic)

            self.channel.basic_publish(exchange=MQConstants.topicExchangeFromAdmin,
                                       routing_key="".join([str(expert_id), ".", Task.set_community_best]),
                                       properties=pika.BasicProperties(type="task", delivery_mode=2),
                                       body=message)
            print("I've just sent the message to agent #{}: {}".format(str(expert_id), message))

        message = {}
        self.broadcast_task_msg(task=Task.set_community_best, message_dic=message)

        self.wait_for_agents(before_message="Wait until everyone shares his estimates",
                             after_message="Experts were notified about the community_best! Ready to go!")

        message = {}
        self.broadcast_task_msg(task=Task.finish_game, message_dic=message)

        self.wait_for_agents(before_message="Wait until everyone leaves the room",
                             after_message="Experts left the room! Bye!")

        os._exit(1)


if __name__ == '__main__':
    maker = RMQDecisionMaker()
    maker.start_game()
