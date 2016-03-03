class TwoTuple:
    def __init__(self,term,alpha,position):
        self.term = term
        self.alpha = alpha
        self.position = position

    def get_term(self):
        return self.term

    def get_alpha(self):
        return self.alpha

    #############################################################################################
    # System functions overriding
    #############################################################################################

    def __eq__(self, other):
        if((other.__dict__.get("term",0) and other.term  == self.term) and
               (other.__dict__.get("alpha",False)  is not False and other.alpha  == self.alpha)):
            return True
        else:
            return False

    def __str__(self):
        return "[<TwoTuple>: term={},alpha={}]".format(self.term,self.alpha)

    def __repr__(self):
        return "<<TwoTuple>: term={},alpha={}>".format(self.term,self.alpha)

    def __gt__(self, other):
        if self.position > other.position:
            return True
        elif self.position < other.position:
            return False
        else:
            # so their labels are the same
            if self.__eq__(other):
                return False
            elif self.alpha > other.alpha:
                return True
            else:
                return False