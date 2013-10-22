from .square import Square


class Go(Square):
    '''
    Represents the Go square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.GO)


