import random


class Expert():
    def __init__(self,name):
        self.name = name
        self.alternatives = []
        self.estimates = []
        self.options = []

    def set_alternatives(self,alternatives):
        self.alternatives = alternatives[:]

    def get_alternatives(self):
        return self.alternatives

    def calculate_estimates(self):
        assert self.alternatives, "Alternatives should not be empty"
        assert self.options, "Options should not be empty"
        self.estimates = [random.choice(self.options) for i in self.alternatives]

    def get_estimates(self):
        return self.estimates

    def set_estimate_options(self,options):
        assert options, "Options should not be empty"
        self.options = options


if __name__ == '__main__':
    print('Starting to initialize the expert')
    e = Expert("expert1")
    options = ["good","bad","excellent","satisfactory"]
    e.set_estimate_options(options)
    alt = [chr(i) for i in range(4)]
    e.set_alternatives(alt)
    e.calculate_estimates()
    print(e.get_estimates())