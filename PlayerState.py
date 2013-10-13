
class PlayerState(object):
    '''
    Holds data for one player, such as the amount of money that have and
    which properties they own.

    Note 1: The player algorithm is not in this class (or in a derived class).

    Note 2: When player-state is passed to other players, some of the data is
            blanked out, such as the amount of money owned.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.square = 0
        self.cash = 0
        self.properties = []


