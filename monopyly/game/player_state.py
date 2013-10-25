import copy


class PlayerState(object):
    '''
    Holds data for one player, such as the amount of money that have and
    which properties they own.

    Note: The player algorithm is not in this class (or in a derived class).
    '''

    def __init__(self, player_number):
        '''
        The 'constructor'.
        '''
        self.square = 0
        self.cash = 1500
        self.properties = []
        self.number_of_get_out_of_jail_free_cards = 0
        self.player_number = player_number

    def copy(self):
        '''
        Returns a copy of the player state.
        '''
        return copy.deepcopy(self)