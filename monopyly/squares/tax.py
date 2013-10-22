from .square import Square


class Tax(Square):
    '''
    Represents the Income Tax and Super Tax squares.
    '''

    def __init__(self, name, tax):
        '''
        The 'constructor'.
        '''
        super().__init__(name)
        self.tax = tax


