from monopyly.squares.property_set import PropertySet
from .property import Property
from .street import Street
from .square import Square


class Station(Property):
    '''
    Represents a station.
    '''

    def __init__(self, name, property_set):
        '''
        The 'constructor'.
        '''
        super().__init__(name, property_set, 200)

    def calculate_rent(self, game, player):
        '''
        The rent depends on how many station the owner owns.
        '''
        # We find how many stations the owner has...
        board = game.state.board
        owned_stations = board.get_property_set(PropertySet.STATION).intersection(self.owner.state.properties)
        number_of_owned_stations = len(owned_stations)

        if number_of_owned_stations == 1:
            return 25
        elif number_of_owned_stations == 2:
            return 50
        elif number_of_owned_stations == 3:
            return 100
        elif number_of_owned_stations == 4:
            return 200

        return 0

