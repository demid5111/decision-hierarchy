import random

from supporting.primitives import print_list, print_dictionary
from two_tuple.base.decisioner import Decisioner
from two_tuple.base.linguistic_set import LinguisticSet
from two_tuple.base.two_tuple import TwoTuple


class LHDecisionMaker(Decisioner):
    NUM_EXPERTS = 3
    NUM_ALTERNATIVES = 3

    def __init__(self):
        super().__init__()
        self._linguistic_sets = {}
        self._best_set = -1
        self.results = []

    def retrieve_sets(self):
        size = 3
        for i in range(LHDecisionMaker.NUM_EXPERTS):
            self._linguistic_sets[i] = LinguisticSet(["_".join(["good", str(i), str(j)]) for j in range(size)])
            size = size * 2 - 1

    def define_alternatives(self):
        self.alternatives = [chr(i + 50) for i in range(LHDecisionMaker.NUM_ALTERNATIVES)]

    def retrieve_estimates(self):
        assert self.alternatives, "Alternatives should be a non empty list"
        # here we have that e.g. expert #1 has set #3
        self.expert_to_set = {0: 2,
                              1: 0,
                              2: 1}
        self.results = [
            [random.choice(self.linguistic_sets[self.expert_to_set[i]]) for i in range(len(self.alternatives))]
            for i in self.expert_to_set.keys()
            ]

    def choose_best_set(self):
        try:
            self._best_set = sorted(self._linguistic_sets.keys(), key=lambda x: int(x), reverse=True)[0]
        except KeyError:
            raise KeyError

    def symbolic_aggregation_operator(self, number):
        new_num = round(number)
        if new_num >= len(self.options):
            raise IndexError
        term = self.estimates_map_reverse[new_num]
        alpha = round(number - self.estimates_map[term], 2)
        return TwoTuple(term=term, alpha=alpha, position=new_num)

    def symbolic_aggregation_operator_reverse(self, two_tuple):
        term = two_tuple.get_term()
        alpha = two_tuple.get_alpha()
        return self.estimates_map[term] + alpha

    def transform_to_level(self, source_level, target_level, two_tuple):
        new_num = (self.symbolic_aggregation_operator_reverse(two_tuple) * target_level.size - 1) / (
            source_level.size - 1)
        return self.symbolic_aggregation_operator(new_num)

    def lh_two_tuple_decision(self):
        if not self.estimates_map:
            self.map_estimates_to_integers()

        # 1. first create matrix of 2-tuples from original term sets
        self.matrix = self.make_matrix_two_tuples()

        # 2. now convert it into the single set which is the best representative
        if not self.best_set:
            self.choose_best_set()
        self.matrix = self.make_normlized_matrix_two_tuples()

        # 3. calculate total average values by alternative
        res = self.calculate_total_by_alternative()

        # 4. choose best alternative so far
        res = sorted(res, reverse=True)[0]

        # 5. transform the value of best alternatives into the set of understandable values for all experts
        # TODO: add this transformation
        return res

    def make_matrix_two_tuples(self):
        """
        Initial normalization step
        :return:
        """
        assert self.expert_to_set, "Experts should have already shared their estimates"
        matrix = []
        k = 0
        for i in self.expert_to_set.keys():
            row = []
            for j in self.results[k]:
                row.append(
                        TwoTuple(term=j, alpha=0,
                                 position=self.linguistic_sets[self.expert_to_set[i]].estimates_map[j]))
            matrix.append(row)
            k += 1
        return matrix

    def make_normlized_matrix_two_tuples(self):
        assert self.matrix, "Matrix initial should not be empty"
        for (expert, row) in enumerate(self.matrix):
            for (alternative, ttuple) in row:
                self.matrix[expert][alternative] = self.transform_to_level(self.linguistic_sets[expert].size,
                                                                           self.best_set.size,
                                                                           self.matrix[expert][alternative])

    @property
    def linguistic_sets(self):
        return self._linguistic_sets

    @property
    def best_set(self):
        return self._best_set


if __name__ == '__main__':
    maker = LHDecisionMaker()
    maker.retrieve_sets()
    print_dictionary(maker.linguistic_sets)
    maker.choose_best_set()
    print("best option: " + str(maker.best_set))

    maker.define_alternatives()
    maker.retrieve_estimates()
    maker.lh_two_tuple_decision()

    print(maker.transform_to_level(maker.linguistic_sets[0], maker.linguistic_sets[maker.best_set],
                                   TwoTuple("good_1_5", 0, 5)))
