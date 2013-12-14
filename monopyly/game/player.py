from .player_state import PlayerState
from ..squares import Property, Street


class Player(object):
    '''
    Holds the PlayerState and a player AI (an object
    derived from PlayerAIBase).
    '''

    def __init__(self, ai, board):
        '''
        The 'constructor'.
        '''
        self.state = PlayerState()
        self.ai = ai
        self.board = board

    def owns_properties(self, property_names):
        '''
        Returns True if this player owns all the properties passed in,
        False if not (or if any of the squares passed in are no properties).
        '''
        # We check each property...
        for property_name in property_names:
            square = self.board.get_square_by_name(property_name)

            # We check that the square is a property...
            if not isinstance(square, Property):
                return False

            if square.owner is not self:
                return False

        return True

    @property
    def net_worth(self):
        '''
        Returns the player's net worth, which includes their
        cash, properties and houses.
        '''
        # Net worth includes cash...
        total = self.state.cash

        for property in self.state.properties:
            # We add the mortgage value of properties...
            total += property.mortgage_value

            # We add the resale value of houses...
            if type(property) == Street:
                total += int(property.house_price/2 * property.number_of_houses)

        return total

    @property
    def name(self):
        '''
        Returns the player name.
        '''
        return self.ai.get_name()

    def is_same_player(self, other):
        '''
        Returns true if the other player is the same as this one.

        'other' can be either a Player object or a Player AI object.
        '''
        if other is self:
            return True

        if other is self.ai:
            return True

        return False