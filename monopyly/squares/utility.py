from .property import Property
from .property_set import PropertySet
from .square import Square


class Utility(Property):
    '''
    Represents the utilities (Water Works and Electric Company).
    '''

    def __init__(self, name, property_set):
        '''
        The 'constructor'
        '''
        super().__init__(name, property_set, 150)

    def calculate_rent(self, game, player):
        '''
        The rent is 4x the roll of the dice if the owner has
        one utility, 10x if they have both.
        '''
        # We find how many utilities the owner has...
        board = game.state.board
        owned_utilities = board.get_property_set(PropertySet.UTILITY).intersection(self.owner.state.properties)
        number_of_owned_utilities = len(owned_utilities)

        if number_of_owned_utilities == 1:
            return 4 * game.most_recent_total_dice_roll
        elif number_of_owned_utilities == 2:
            return 10 * game.most_recent_total_dice_roll

        return 0




