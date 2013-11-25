from .player_state import PlayerState
from ..squares import Property, Street


class Player(object):
    '''
    Holds the PlayerState and a player AI (an object
    derived from PlayerAIBase).
    '''

    def __init__(self, ai, player_number, board):
        '''
        The 'constructor'.
        '''
        self.state = PlayerState(player_number)
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

            if square.owner_player_number != self.state.player_number:
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

        for property_index in self.state.property_indexes:
            # We add the mortgage value of properties...
            property = self.board.get_square_by_index(property_index)
            total += property.mortgage_value

            # We add the resale value of houses...
            if type(property) == Street:
                total += (property.house_price/2 * property.number_of_houses)

        return total
