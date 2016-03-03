import unittest

from decision_maker import DecisionMaker
from two_tuple import TwoTuple

class TwoTupleTest(unittest.TestCase):
    def test_sorting(self):
        res = [TwoTuple("term6",0.25,6),TwoTuple("term5",0,5),TwoTuple("term5",-0.25,5),TwoTuple("term4",0.5,4)]
        self.assertEqual(res, sorted(res,reverse=True))

class DesicionMakerSupportingsTest(unittest.TestCase):
    def setUp(self):
        self.maker = DecisionMaker()
        self.maker.options = ["bad","satisfactory","good","excellent"]
        self.maker.map_estimates_to_integers()

    def test_symbolic_operator_correct(self):
        self.assertEqual(TwoTuple("good",-0.2,2),
                         self.maker.symbolic_aggregation_operator(1.8),
                         "1.8  means (good,-0.2)")

    def test_symbolic_operator_raisesException(self):
        with self.assertRaises(IndexError):
            self.maker.symbolic_aggregation_operator(3.8)

    def test_symbolic_operator_reverse_correct(self):
        self.assertEqual(1.8,
                         self.maker.symbolic_aggregation_operator_reverse(TwoTuple("good",-0.2,2)),
                         "(good,-0.2) means 1.8")

    def tearDown(self):
        del self.maker

class DecisionMakerTest(unittest.TestCase):
    def setUp(self):
        self.maker = DecisionMaker()
        self.maker.options = ["term0","term1","term2","term3","term4","term5","term6","term7","term8"]
        self.maker.map_estimates_to_integers()
        self.maker.results = [["term4","term6","term3","term5"],
                              ["term5","term6","term5","term5"],
                              ["term5","term8","term8","term5"],
                              ["term4","term5","term3","term5"]]
        self.maker.matrix = [[TwoTuple("term4",0,4),TwoTuple("term6",0,6),TwoTuple("term3",0,3),TwoTuple("term5",0,5)],
                              [TwoTuple("term5",0,5),TwoTuple("term6",0,6),TwoTuple("term5",0,5),TwoTuple("term5",0,5)],
                              [TwoTuple("term5",0,5),TwoTuple("term8",0,8),TwoTuple("term8",0,8),TwoTuple("term5",0,5)],
                              [TwoTuple("term4",0,4),TwoTuple("term5",0,5),TwoTuple("term3",0,3),TwoTuple("term5",0,5)]]

    def test_two_tuples_decision_root_make_initial_matrix(self):
        self.assertEqual(self.maker.matrix, self.maker.make_matrix_two_tuples())

    def test_two_tuples_decision_calculate_estimates_by_alternative(self):
        res = [TwoTuple("term4",0.5,4),TwoTuple("term6",0.25,6),TwoTuple("term5",-0.25,5),TwoTuple("term5",0,5)]
        self.assertEqual(res, self.maker.calculate_total_by_alternative())

    def test_two_tuples_decision_final_decision(self):
        res = TwoTuple("term6",0.25,6)
        self.assertEqual(res, self.maker.two_tuples_decision())

    def tearDown(self):
        del self.maker


if __name__ == '__main__':
    unittest.main()