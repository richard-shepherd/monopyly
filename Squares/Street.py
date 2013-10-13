from collections import namedtuple

from . import Property


class Street(Property):
    '''
    A type of Property representing a street.

    Manages rents, house-building and so on.
    '''

    class Rents(namedtuple("Rents", "base whole_set one_house two_houses three_houses four_houses hotel")):
        '''
        Holds the various rents for a Street property.
        '''
        pass

    def __init__(self, name, street_set, price, mortgage_value, house_price, rents):
        '''
        The 'constructor'.

        rents: passed in as a Rents object (a namedtuple).
        '''
        # The base class holds the values applicable to all properties...
        super(Street, self).__init__(name, street_set, price)

        # We hold the ones specific to streets...
        self.mortgage_value = mortgage_value
        self.house_price = house_price
        self.rents = rents

