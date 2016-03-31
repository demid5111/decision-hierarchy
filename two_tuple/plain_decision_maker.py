import random

import pika

from supporting.primitives import print_list, print_dictionary
from two_tuple.base.two_tuple import TwoTuple


class DecisionMaker:
    NUM_ALTERNATIVES = 4
    NUM_EXPERTS = 4

    def __init__(self):
        self.options = []
        self.alternatives = []
        self.results = []
        self.host = 'localhost'
        self.estimates_map = {}  # "good":2
        self.estimates_map_reverse = {}  # 2:"good
        self.matrix = []  # here we put calculated two-tuples for the raw data from experts

    def define_estimate_options(self):
        self.options = ["bad", "satisfactory", "good", "excellent"]

    def define_alternatives(self):
        self.alternatives = [chr(i + 50) for i in range(DecisionMaker.NUM_ALTERNATIVES)]

    def get_estimates_from_experts(self):
        # TODO: make retrieval real
        self.results = [
            [random.choice(self.options) for i in range(len(self.alternatives))]
            for i in range(DecisionMaker.NUM_EXPERTS)
            ]
        return self.results

    def two_tuples_decision(self):
        if not self.estimates_map:
            self.map_estimates_to_integers()
        self.matrix = self.make_matrix_two_tuples()
        res = self.calculate_total_by_alternative()
        res = sorted(res, reverse=True)
        return res[0]

    def map_estimates_to_integers(self):
        assert self.options, "Options should not be empty"
        for (i, val) in enumerate(self.options):
            self.estimates_map[val] = i
            self.estimates_map_reverse[i] = val

    def get_map_estimates(self):
        return self.estimates_map

    def symbolic_aggregation_operator(self, number):
        assert self.options, "Options should not be null"
        new_num = round(number)
        if new_num >= len(self.options):
            raise IndexError
        term = self.estimates_map_reverse[new_num]
        alpha = round(number - self.estimates_map[term], 2)
        return TwoTuple(term=term, alpha=alpha, position=new_num)

    def symbolic_aggregation_operator_reverse(self, two_tuple):
        assert self.options, "Options should not be null"
        term = two_tuple.get_term()
        alpha = two_tuple.get_alpha()
        return self.estimates_map[term] + alpha

    def make_matrix_two_tuples(self):
        """
        Initial normalization step
        :return:
        """
        matrix = []
        for i in self.results:
            row = []
            for j in i:
                row.append(TwoTuple(term=j, alpha=0, position=self.estimates_map[j]))
            matrix.append(row)
        return matrix

    def calculate_total_by_alternative(self):
        sum = 0
        res_dic = {}
        for row in self.matrix:
            for (j, val) in enumerate(row):
                try:
                    res_dic[j] += self.symbolic_aggregation_operator_reverse(val)
                except KeyError:
                    res_dic[j] = self.symbolic_aggregation_operator_reverse(val)
        res = [self.symbolic_aggregation_operator(j / len(res_dic.keys())) for (i, j) in res_dic.items()]
        return res


if __name__ == "__main__":
    print('Starting to initialize the Decision Maker')
    maker = DecisionMaker()
    maker.define_estimate_options()
    maker.define_alternatives()
    estimates = maker.get_estimates_from_experts()
    print("Got estimates from agents: ")
    print_list(estimates)

    maker.map_estimates_to_integers()
    print("Mapped estimates: ")
    print_dictionary(maker.get_map_estimates())

    maker.two_tuples_decision()
