__author__ = "Demidovskij Alexander"
__copyright__ = "Copyright 2016, ML-MA-LDM Project"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "monadv@yandex.ru"
__status__ = "Development"

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

