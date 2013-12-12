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
        self._station_indexes = set()

    def calculate_rent(self, game, player):
        '''
        The rent depends on how many station the owner owns.
        '''
        # We find how many stations the owner has...
        self._find_station_indexes(game.state.board)
        owner = self.owner
        owned_stations = set.intersection(self._station_indexes, owner.state.property_indexes)
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

    def _find_station_indexes(self, board):
        '''
        Finds the set of board-indexes for the stations.
        '''
        if len(self._station_indexes) != 0:
            return
        self._station_indexes.add(board.get_index(Square.Name.KINGS_CROSS_STATION))
        self._station_indexes.add(board.get_index(Square.Name.MARYLEBONE_STATION))
        self._station_indexes.add(board.get_index(Square.Name.FENCHURCH_STREET_STATION))
        self._station_indexes.add(board.get_index(Square.Name.LIVERPOOL_STREET_STATION))

