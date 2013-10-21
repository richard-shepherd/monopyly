from .property import Property
from .street import Street


class Station(Property):
    '''
    Represents a station.
    '''

    def __init__(self, name):
        '''
        The 'constructor'.
        '''
        super(Station, self).__init__(name=name, street_set=Street.Set.STATION, price=200)


