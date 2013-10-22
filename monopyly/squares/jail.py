from .square import Square


class Jail(Square):
    '''
    Represents the Jail / Just Visiting square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.JAIL)

