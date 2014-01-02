import copy
from ..squares import Street


class PlayerState(object):
    '''
    Holds data for one player, such as the amount of money that have and
    which properties they own.

    Note: The player algorithm is not in this class (or in a derived class).
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''

        # The square the player is currently on (0 = Go, 39 = Mayfair etc).
        # This can be used as an index into the squares property of the board...
        self.square = 0

        # The amount of money owned by the player...
        self.cash = 1500

        # The collection of properties owned by the player.
        # These are objects derived from the Property class.
        self.properties = set()

        # Get Out Of Jail Free cards the player is holding...
        self.get_out_of_jail_free_cards = []

        # Whether the player is in jail, and if so how many turns they
        # have been there...
        self.is_in_jail = False
        self.number_of_turns_in_jail = 0

        # The collection of complete sets owned by this player.
        # The items in the collection are PropertySet objects.
        self.owned_sets = set()

        # The collection of complete unmortgaged sets owned by this player.
        # The items in the collection are PropertySet objects.
        self.owned_unmortgaged_sets = set()

        # AIs are given a limited amount of processing time per game...
        self.ai_processing_seconds_remaining = 60.0

    def get_number_of_houses_and_hotels(self, board):
        '''
        Returns the number of houses and hotels owned by this player.
        '''
        number_of_houses = 0
        number_of_hotels = 0
        for property in self.properties:
            # We check if the property is a street (ie, not a station or utility)...
            if type(property) != Street:
                continue

            if property.number_of_houses == 5:
                # Five houses is a hotel...
                number_of_hotels += 1
            else:
                number_of_houses += property.number_of_houses

        return number_of_houses, number_of_hotels

    @property
    def number_of_get_out_of_jail_free_cards(self):
        '''
        The number of GOOJF cards the player has.
        '''
        return len(self.get_out_of_jail_free_cards)


