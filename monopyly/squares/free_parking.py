from .square import Square


class FreeParking(Square):
    '''
    Represents the Free Parking square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.FREE_PARKING)

