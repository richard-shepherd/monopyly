
class Property(object):
    '''
    A base class for properties, which manages some common features
    of them.

    This include holding whether the property is owned (and if so, who by)
    and whether the property is mortgaged.

    Derived classes are: Street, Station, Utility.
    '''

    class StreetSet(object):
        '''
        An 'enum' for the different property sets.
        '''
        INVALID = 0
        BROWN = 1
        LIGHT_BLUE = 2
        PURPLE = 3
        ORANGE = 4
        RED = 5
        YELLOW = 6
        GREEN = 7
        DARK_BLUE = 8
        STATION = 9
        UTILITY = 10


    def __init__(self, name, street_set, price, mortgage_value):
        '''
        The 'constructor'.
        '''
        self.name = name
        self.street_set = street_set
        self.price = price
        self.mortgage_value = mortgage_value
        self.mortgaged = False
        self.owner = None




