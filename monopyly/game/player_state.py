import copy
from ..squares import Street


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
        self.in_jail = False
        self.number_of_turns_in_jail = 0

    def copy(self):
        '''
        Returns a copy of the player state.
        '''
        return copy.deepcopy(self)

    def get_number_of_houses_and_hotels(self):
        '''
        Returns the number of houses and hotels owned by this player.
        '''
        number_of_houses = 0
        number_of_hotels = 0
        for property in self.properties:
            # Only streets have houses or hotels...
            if(type(property) != Street):
                continue
            number_of_houses += property.number_of_houses
            number_of_hotels += (1 if property.has_hotel else 0)

        return number_of_houses, number_of_hotels




