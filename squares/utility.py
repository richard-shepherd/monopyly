from .property import Property


class Utility(Property):
    '''
    Represents the utilities (Water Works and Electric Company).
    '''

    def __init__(self, name):
        '''
        The 'constructor'
        '''
        super(Utility, self).__init__(name=name, street_set=Property.Set.UTILITY, price=150)


