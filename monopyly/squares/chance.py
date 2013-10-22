from .square import Square


class Chance(Square):
    '''
    Represents one of the Chance squares.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.CHANCE)

