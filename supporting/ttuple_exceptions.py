class OptionsListEmptyError(Exception):
    def __init__(self,message="Options list must not be empty!"):
        self.message = message

    def __str__(self):
        return self.message

class UnexpectedMessageError(Exception):
    def __init__(self,message="Got unexpected message"):
        self.message = message

    def __str__(self):
        return self.message

