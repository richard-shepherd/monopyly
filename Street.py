from Property import *
from collections import namedtuple


class Street(Property):
    '''
    A type of Property representing a street.

    Manages rents, house-building and so on.
    '''

    Rents = namedtuple("Rents", "base_rent set_rent ") # TODO: add house rents

    def __init__(self, name, set, price, mortgage_value, house_price, rents):
        '''
        The 'constructor'.

        rents: passed in as a Rents namedtuple
        '''


