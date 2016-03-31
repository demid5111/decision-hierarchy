import abc
import random
import sys
from .two_tuple import TwoTuple


class Decisioner:
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

    @abc.abstractmethod
    def define_estimate_options(self):
        raise NotImplementedError

    @abc.abstractmethod
    def define_alternatives(self):
        raise NotImplementedError

    def get_estimates_from_experts(self):
        # TODO: make retrieval real
        self.results = [
            [random.choice(self.options) for i in range(len(self.alternatives))]
            for i in range(Decisioner.NUM_EXPERTS)
            ]
        return self.results

    @abc.abstractmethod
    def two_tuples_decision(self):
        raise NotImplementedError

    @abc.abstractmethod
    def map_estimates_to_integers(self):
        raise NotImplementedError

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

    @abc.abstractmethod
    def calculate_total_by_alternative(self):
        raise NotImplementedError


if __name__ == "__main__":
    sys.exit(print("Not available for running in console"))
