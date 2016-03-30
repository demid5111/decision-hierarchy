from supporting.ttuple_exceptions import OptionsListEmptyError


class LinguisticSet:
    def __init__(self, options=None):
        if not options:
            raise OptionsListEmptyError
        self._options = options
        self._size = len(self._options)
        self._estimates_map = {}
        self._estimates_map_reverse = {}
        self.__map_estimates_to_integers()

    def __map_estimates_to_integers(self):
        assert self._options, "Options should not be empty"
        for (i, val) in enumerate(self._options):
            self._estimates_map[val] = i
            self._estimates_map_reverse[i] = val

    @property
    def estimates_map(self):
        assert self._estimates_map, "Estimates map should not be null"
        return self._estimates_map

    @property
    def estimates_map_reverse(self):
        assert self._estimates_map, "Estimates map (reverse) should not be null"
        return self._estimates_map_reverse

    @property
    def size(self):
        return self._size

    def __str__(self):
        return "<{}>. Size: {}".format(LinguisticSet.__class__.__name__,self._size)

    def __repr__(self):
        return "<{}>. Size: {}".format(LinguisticSet.__class__.__name__,self._size)
