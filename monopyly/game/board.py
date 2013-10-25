from ..squares import *


class Board(object):
    '''
    Represents the board.

    Holds a collection of objects which each implement the
    Square interface, as well as the collection of Chance
    and Community Chest cards.
    '''

    # A constant for the number of squares on the board...
    NUMBER_OF_SQUARES = 40

    def __init__(self):
        '''
        The 'constructor'.
        '''
        # We add the collection of squares to the board...
        self.squares = []
        self.add_squares_to_board()

        # We map the square names to their positions on the board...
        self._name_to_index_map = {}
        self.map_names_to_indexes()

    def add_squares_to_board(self):
        '''
        Sets up the collection of squares that make up the board.
        '''
        # Go...
        self.squares.append(Go())

        # Old Kent Road...
        self.squares.append(
            Street(name=Property.Name.OLD_KENT_ROAD,
                   street_set=Property.Set.BROWN,
                   price=60,
                   house_price=50,
                   rents=Street.Rents(2, 10, 30, 90, 160, 250)))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Whitechapel Road...
        self.squares.append(
            Street(name=Property.Name.WHITECHAPEL_ROAD,
                   street_set=Property.Set.BROWN,
                   price=60,
                   house_price=50,
                   rents=Street.Rents(4, 20, 60, 180, 320, 450)))

        # Income tax...
        self.squares.append(Tax(name=Property.Name.INCOME_TAX, tax=200))

        # Kings Cross...
        self.squares.append(Station(name=Property.Name.KINGS_CROSS_STATION))

        # The Angel Islington...
        self.squares.append(
            Street(name=Property.Name.THE_ANGEL_ISLINGTON,
                   street_set=Property.Set.LIGHT_BLUE,
                   price=100,
                   house_price=50,
                   rents=Street.Rents(6, 30, 90, 270, 400, 550)))

        # Chance...
        self.squares.append(Chance())

        # Euston Road
        self.squares.append(
            Street(name=Property.Name.EUSTON_ROAD,
                   street_set=Property.Set.LIGHT_BLUE,
                   price=100,
                   house_price=50,
                   rents=Street.Rents(6, 30, 90, 270, 400, 550)))

        # Pentonville Road...
        self.squares.append(
            Street(name=Property.Name.PENTONVILLE_ROAD,
                   street_set=Property.Set.LIGHT_BLUE,
                   price=120,
                   house_price=50,
                   rents=Street.Rents(8, 40, 100, 300, 450, 600)))

        # Jail...
        self.squares.append(Jail())

        # Pall Mall...
        self.squares.append(
            Street(name=Property.Name.PALL_MALL,
                   street_set=Property.Set.PURPLE,
                   price=140,
                   house_price=100,
                   rents=Street.Rents(10, 50, 150, 450, 625, 750)))

        # Electric Company...
        self.squares.append(Utility(Property.Name.ELECTRIC_COMPANY))

        # Whitehall...
        self.squares.append(
            Street(name=Property.Name.WHITEHALL,
                   street_set=Property.Set.PURPLE,
                   price=140,
                   house_price=100,
                   rents=Street.Rents(10, 50, 150, 450, 625, 750)))

        # Northumberland Avenue...
        self.squares.append(
            Street(name=Property.Name.NORTHUMBERLAND_AVENUE,
                   street_set=Property.Set.PURPLE,
                   price=160,
                   house_price=100,
                   rents=Street.Rents(12, 60, 180, 500, 700, 900)))

        # Marylebone Station...
        self.squares.append(Station(name=Property.Name.MARYLEBONE_STATION))

        # Bow Street...
        self.squares.append(
            Street(name=Property.Name.BOW_STREET,
                   street_set=Property.Set.ORANGE,
                   price=180,
                   house_price=100,
                   rents=Street.Rents(14, 70, 200, 550, 750, 950)))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Marlborough Street...
        self.squares.append(
            Street(name=Property.Name.MARLBOROUGH_STREET,
                   street_set=Property.Set.ORANGE,
                   price=180,
                   house_price=100,
                   rents=Street.Rents(14, 70, 200, 550, 750, 950)))

        # Vine Street...
        self.squares.append(
            Street(name=Property.Name.VINE_STREET,
                   street_set=Property.Set.ORANGE,
                   price=200,
                   house_price=100,
                   rents=Street.Rents(16, 80, 220, 600, 800, 1000)))

        # Free Parking...
        self.squares.append(FreeParking())

        # Strand...
        self.squares.append(
            Street(name=Property.Name.STRAND,
                   street_set=Property.Set.RED,
                   price=220,
                   house_price=150,
                   rents=Street.Rents(18, 90, 250, 700, 875, 1050)))

        # Chance...
        self.squares.append(Chance())

        # Fleet Street...
        self.squares.append(
            Street(name=Property.Name.FLEET_STREET,
                   street_set=Property.Set.RED,
                   price=220,
                   house_price=150,
                   rents=Street.Rents(18, 90, 250, 700, 875, 1050)))

        # Trafalgar Square...
        self.squares.append(
            Street(name=Property.Name.TRAFALGAR_SQUARE,
                   street_set=Property.Set.RED,
                   price=240,
                   house_price=150,
                   rents=Street.Rents(20, 100, 300, 750, 925, 1100)))

        # Fenchurch Street Station...
        self.squares.append(Station(name=Property.Name.FENCHURCH_STREET_STATION))

        # Leicester Square...
        self.squares.append(
            Street(name=Property.Name.LEICESTER_SQUARE,
                   street_set=Property.Set.YELLOW,
                   price=260,
                   house_price=150,
                   rents=Street.Rents(22, 110, 330, 800, 975, 1150)))

        # Coventry Street...
        self.squares.append(
            Street(name=Property.Name.COVENTRY_STREET,
                   street_set=Property.Set.YELLOW,
                   price=260,
                   house_price=150,
                   rents=Street.Rents(22, 110, 330, 800, 975, 1150)))

        # Water Works...
        self.squares.append(Utility(Property.Name.WATER_WORKS))

        # Piccadilly...
        self.squares.append(
            Street(name=Property.Name.PICCADILLY,
                   street_set=Property.Set.YELLOW,
                   price=280,
                   house_price=150,
                   rents=Street.Rents(22, 120, 360, 850, 1025, 1200)))

        # Go To Jail...
        self.squares.append(GoToJail())

        # Regent Street...
        self.squares.append(
            Street(name=Property.Name.REGENT_STREET,
                   street_set=Property.Set.GREEN,
                   price=300,
                   house_price=200,
                   rents=Street.Rents(26, 130, 390, 900, 1100, 1275)))

        # Oxford Street...
        self.squares.append(
            Street(name=Property.Name.OXFORD_STREET,
                   street_set=Property.Set.GREEN,
                   price=300,
                   house_price=200,
                   rents=Street.Rents(26, 130, 390, 900, 1100, 1275)))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Bond Street...
        self.squares.append(
            Street(name=Property.Name.BOND_STREET,
                   street_set=Property.Set.GREEN,
                   price=320,
                   house_price=200,
                   rents=Street.Rents(28, 150, 450, 1000, 1200, 1400)))

        # Liverpool Street Station...
        self.squares.append(Station(Property.Name.LIVERPOOL_STREET_STATION))

        # Chance...
        self.squares.append(Chance())

        # Park Lane...
        self.squares.append(
            Street(name=Property.Name.PARK_LANE,
                   street_set=Property.Set.DARK_BLUE,
                   price=350,
                   house_price=200,
                   rents=Street.Rents(35, 175, 500, 1100, 1300, 1500)))

        # Super Tax...
        self.squares.append(Tax(name=Property.Name.SUPER_TAX, tax=100))

        # Mayfair...
        self.squares.append(
            Street(name=Property.Name.MAYFAIR,
                   street_set=Property.Set.DARK_BLUE,
                   price=400,
                   house_price=200,
                   rents=Street.Rents(50, 200, 600, 1400, 1700, 2000)))

    def map_names_to_indexes(self):
        '''
        Maps the square names to their (zero-based) indexes on the board.

        Each name maps to a list of locations, as some square names (Chance
        and Community Chest) have multiple squares on the board.
        '''
        for index in range(len(self.squares)):
            name = self.squares[index].name
            if(name not in self._name_to_index_map):
                self._name_to_index_map[name] = []
            self._name_to_index_map[name].append(index)

    def move_player(self, player, number_of_squares):
        '''
        Advances the player by the number of squares passed in.

        Returns the square landed on.
        '''
        player.state.square += number_of_squares
        if(player.state.square >= Board.NUMBER_OF_SQUARES):
            player.state.square -= Board.NUMBER_OF_SQUARES

        square = self.squares[player.state.square]
        return square

    def get_index(self, square_name):
        '''
        Returns the zero-based index (ie, the board position)
        for the square passed in.

        Note that this is returned as a list, as some names have more
        than one location.
        '''
        return self._name_to_index_map[square_name]
