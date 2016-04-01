import random

from supporting.primitives import print_list, print_dictionary
from two_tuple.base.decisioner import Decisioner
from two_tuple.base.linguistic_set import LinguisticSet
from two_tuple.base.two_tuple import TwoTuple


class LHDecisionMaker(Decisioner):
    NUM_EXPERTS = 4
    NUM_ALTERNATIVES = 4
    NUM_SETS = 6

    def __init__(self):
        super().__init__()
        self._linguistic_sets = {}
        self._best_set = -1
        self.results = {}
        self.expert_to_set_id = {}

    def retrieve_sets(self):
        size = 3
        for i in range(LHDecisionMaker.NUM_SETS):
            self._linguistic_sets[i] = LinguisticSet(["_".join(["good", str(size), str(j)]) for j in range(size)])
            size = size * 2 - 1

    def get_set_id_by_size(self, size):
        id = -1
        for (index, lset) in self.linguistic_sets.items():
            if lset.size == size:
                id = index
        return id

    def define_alternatives(self):
        self.alternatives = [chr(i + 50) for i in range(LHDecisionMaker.NUM_ALTERNATIVES)]

    def set_experts_map(self):
        self.expert_to_set_id = {0: 2,
                                 1: 1,
                                 2: 0,
                                 3: 2}
    def retrieve_estimates(self):
        assert self.alternatives, "Alternatives should be a non empty list"
        # here we have that e.g. expert #1 has set #3
        self.set_experts_map()
        for i in self.expert_to_set_id.keys():
            self.results[i] = [random.choice(self.linguistic_sets[self.expert_to_set_id[i]].options)
                     for j in range(len(self.alternatives))]

    def choose_best_set(self):
        try:
            self._best_set = sorted(self._linguistic_sets.keys(), key=lambda x: int(x), reverse=True)[0]
        except KeyError:
            raise KeyError

    def symbolic_aggregation_operator(self, number,source_level_size):
        new_num = round(number)
        term = self.linguistic_set_by_size(source_level_size).estimates_map_reverse[new_num]
        alpha = round(number - self.linguistic_set_by_size(source_level_size).estimates_map[term], 2)
        return TwoTuple(term=term, alpha=alpha, position=new_num)

    def symbolic_aggregation_operator_reverse(self, two_tuple, source_level_size):
        term = two_tuple.get_term()
        alpha = two_tuple.get_alpha()
        return self.linguistic_set_by_size(source_level_size).estimates_map[term] + alpha

    def transform_to_level(self, source_level, target_level, two_tuple):
        if source_level == target_level:
            return two_tuple
        else:
            new_num = (self.symbolic_aggregation_operator_reverse(two_tuple, source_level)
                       * (self.linguistic_set_by_size(target_level).size - 1)) / (
                          self.linguistic_set_by_size(source_level).size - 1)
            return self.symbolic_aggregation_operator(new_num,target_level)

    def translate_ttuple_to_sets(self,two_tuple,source_level_size):
        res = {}
        for (set_id,lset) in self.linguistic_sets.items():
            if source_level_size != self.linguistic_sets[set_id].size:
                new_tuple = self.transform_to_level(
                            source_level_size,
                            self.linguistic_sets[set_id].size,
                            two_tuple)
                res[set_id] = new_tuple
            else:
                res[set_id] = two_tuple
        return res

    def lh_two_tuple_decision(self):
        # 1. first create matrix of 2-tuples from original term sets
        self.matrix = self.make_matrix_two_tuples()

        # 2. now convert it into the single set which is the best representative
        if not self.best_set:
            self.choose_best_set()
        self.make_normalized_matrix_two_tuples()

        # 3. calculate total average values by alternative
        res = self.calculate_total_by_alternative()

        index = res.index(max(res))

        # 4. choose best alternative so far
        res = sorted(res, reverse=True)[0]

        # 5. transform the value of best alternatives into the set of understandable values for all experts
        # TODO: add this transformation
        translations = self.translate_ttuple_to_sets(res,self.linguistic_set_by_id(self.best_set).size)
        return res,index,translations

    def make_matrix_two_tuples(self):
        """
        Initial normalization step
        :return:
        """
        assert self.expert_to_set_id, "Experts should have already shared their estimates"
        matrix = []
        k = 0
        for i in self.expert_to_set_id.keys():
            row = []
            for j in self.results[k]:
                row.append(
                        TwoTuple(term=j, alpha=0,
                                 position=self.linguistic_sets[self.expert_to_set_id[i]].estimates_map[j]))
            matrix.append(row)
            k += 1
        return matrix

    def make_normalized_matrix_two_tuples(self):
        assert self.matrix, "Matrix initial should not be empty"
        for (expert, row) in enumerate(self.matrix):
            for (alternative, ttuple) in enumerate(row):
                self.matrix[expert][alternative] = self.transform_to_level(
                        self.linguistic_sets[self.expert_to_set_id[expert]].size,
                        self.linguistic_sets[self.best_set].size,
                        self.matrix[expert][alternative])

    def calculate_total_by_alternative(self):
        sum = 0
        res_dic = {}
        for row in self.matrix:
            for (j, val) in enumerate(row):
                try:
                    res_dic[j] += self.symbolic_aggregation_operator_reverse(val, self.linguistic_set_by_id(self.best_set).size)
                except KeyError:
                    res_dic[j] = self.symbolic_aggregation_operator_reverse(val, self.linguistic_set_by_id(self.best_set).size)
        res = [self.symbolic_aggregation_operator(j / len(res_dic.keys()), self.linguistic_set_by_id(self.best_set).size) for (i, j) in res_dic.items()]
        return res

    @property
    def linguistic_sets(self):
        return self._linguistic_sets

    @property
    def best_set(self):
        return self._best_set

    def linguistic_set_by_id(self, id):
        return self.linguistic_sets.get(id, None)

    def linguistic_set_by_size(self, size):
        return self.linguistic_set_by_id(self.get_set_id_by_size(size))


if __name__ == '__main__':
    maker = LHDecisionMaker()
    maker.retrieve_sets()
    print_dictionary(maker.linguistic_sets)
    maker.choose_best_set()
    print("best option: " + str(maker.best_set))

    maker.define_alternatives()
    maker.retrieve_estimates()
    res,translations = maker.lh_two_tuple_decision()
    print ("Best option: " + str(res))
    print ("Its translations: " + str(translations))
