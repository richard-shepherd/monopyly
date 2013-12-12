from .property import Property
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
        self._utility_indexes = set()

    def calculate_rent(self, game, player):
        '''
        The rent is 4x the roll of the dice if the owner has
        one utility, 10x if they have both.
        '''
        # We find how many utilities the owner has...
        self._find_utility_indexes(game.state.board)
        owner = self.owner
        owned_utilities = set.intersection(self._utility_indexes, owner.state.property_indexes)
        number_of_owned_stations = len(owned_utilities)

        if number_of_owned_stations == 1:
            return 4 * game.most_recent_total_dice_roll
        elif number_of_owned_stations == 2:
            return 10 * game.most_recent_total_dice_roll

        return 0

    def _find_utility_indexes(self, board):
        '''
        Finds the set of board-indexes for the utilities.
        '''
        if len(self._utility_indexes) != 0:
            return
        self._utility_indexes.add(board.get_index(Square.Name.ELECTRIC_COMPANY))
        self._utility_indexes.add(board.get_index(Square.Name.WATER_WORKS))



