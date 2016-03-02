import random

class DecisionMaker():
    NUM_ALTERNATIVES = 4
    NUM_EXPERTS = 4

    def __init__(self):
        self.options = []
        self.alternatives = []
        self.results = []

    def define_estimate_options(self):
        self.options = ["good","bad","excellent","satisfactory"]

    def define_alternatives(self):
        self.alternatives = [chr(i+50) for i in range(DecisionMaker.NUM_ALTERNATIVES)]

    def get_estimates_from_experts(self):
        # TODO: make retieval real
        self.results = [
            [random.choice(self.options) for i in range(len(self.alternatives))]
            for i in range(DecisionMaker.NUM_EXPERTS)
            ]
        return self.results

def print_list(elements):
    for i in elements:
        print(i)

if __name__ == "__main__":
    print('Starting to initialize the Decision Maker')
    maker = DecisionMaker()
    maker.define_estimate_options()
    maker.define_alternatives()
    estimates = maker.get_estimates_from_experts()
    print("Got estimates from agents: ")
    print_list(estimates)