from ..squares import *
from ..cards import *


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
        # We map the street sets to the collections of properties in them...
        self._property_set_map = dict()
        self._setup_property_sets()

        # We add the collection of squares to the board.
        # This is a list of objects derived from the Square base class.
        # Indexes are: Go = 0, Mayfair = 39 etc.
        self.squares = []
        self._add_squares_to_board()

        # We map the square names to their positions on the board...
        self._name_to_index_map = {}
        self._map_names_to_indexes()

        # The cards...
        self.chance_deck = ChanceDeck()
        self.community_chest_deck = CommunityChestDeck()

    def get_index_list(self, square_name):
        '''
        Returns the zero-based indexes (ie, the board positions)
        for the square passed in.

        Note that this is returned as a list, as some names have more
        than one location.
        '''
        return self._name_to_index_map[square_name]

    def get_index(self, square_name):
        '''
        Returns the zero-based index (ie, the board position)
        for the square passed in.

        For squares with more than one location (Chance and Community
        Chest) this returns the first square.
        '''
        return self._name_to_index_map[square_name][0]

    def get_properties_for_set(self, set_enum):
        '''
        Returns the list of properties in the set passed in.
        '''
        return self.get_property_set(set_enum).properties

    def get_property_set(self, set_enum):
        '''
        Return the PropertySet for the set enum (PropertySet.BROWN, PropertySet.PURPLE etc)
        passed in.
        '''
        return self._property_set_map[set_enum]

    def get_square_by_index(self, index):
        '''
        Returns a square by its index.
        '''
        return self.squares[index]

    def get_square_by_name(self, square_name):
        '''
        Returns a square by its name.
        '''
        index = self.get_index(square_name)
        return self.get_square_by_index(index)

    def get_owned_sets(self):
        '''
        Returns which sets are owned by which players.

        Returned as a dictionary of player to a set of
        property-sets owned by them. For example:
        { player2: {BROWN, PINK}, player4: {YELLOW} }

        The sets are PropertySet objects rather than enums.

        Only players which own a whole unmortgaged set are returned.
        '''
        # We look through the collection of sets...
        results = {}
        for property_set in self._property_set_map.values():
            # Does the set have a unique owner?
            owner = property_set.owner
            if owner is None:
                continue

            # There is a unique owner. We still need to check if all
            # the properties in the set are unmortgaged...
            if not property_set.all_properties_are_unmortgaged:
                continue

            # We add this set to the collection for the owner...
            if owner not in results:
                results[owner] = set()
            results[owner].add(property_set)

        return results

    def _add_squares_to_board(self):
        '''
        Sets up the collection of squares that make up the board.
        '''
        # Go...
        self.squares.append(Go())

        # Old Kent Road...
        self.squares.append(
            Street(name=Square.Name.OLD_KENT_ROAD,
                   property_set=self.get_property_set(PropertySet.BROWN),
                   price=60,
                   house_price=50,
                   rents=[2, 10, 30, 90, 160, 250]))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Whitechapel Road...
        self.squares.append(
            Street(name=Square.Name.WHITECHAPEL_ROAD,
                   property_set=self.get_property_set(PropertySet.BROWN),
                   price=60,
                   house_price=50,
                   rents=[4, 20, 60, 180, 320, 450]))

        # Income tax...
        self.squares.append(Tax(name=Square.Name.INCOME_TAX, tax=200))

        # Kings Cross...
        self.squares.append(
            Station(name=Square.Name.KINGS_CROSS_STATION,
                    property_set=self.get_property_set(PropertySet.STATION)))

        # The Angel Islington...
        self.squares.append(
            Street(name=Square.Name.THE_ANGEL_ISLINGTON,
                   property_set=self.get_property_set(PropertySet.LIGHT_BLUE),
                   price=100,
                   house_price=50,
                   rents=[6, 30, 90, 270, 400, 550]))

        # Chance...
        self.squares.append(Chance())

        # Euston Road
        self.squares.append(
            Street(name=Square.Name.EUSTON_ROAD,
                   property_set=self.get_property_set(PropertySet.LIGHT_BLUE),
                   price=100,
                   house_price=50,
                   rents=[6, 30, 90, 270, 400, 550]))

        # Pentonville Road...
        self.squares.append(
            Street(name=Square.Name.PENTONVILLE_ROAD,
                   property_set=self.get_property_set(PropertySet.LIGHT_BLUE),
                   price=120,
                   house_price=50,
                   rents=[8, 40, 100, 300, 450, 600]))

        # Jail...
        self.squares.append(Jail())

        # Pall Mall...
        self.squares.append(
            Street(name=Square.Name.PALL_MALL,
                   property_set=self.get_property_set(PropertySet.PURPLE),
                   price=140,
                   house_price=100,
                   rents=[10, 50, 150, 450, 625, 750]))

        # Electric Company...
        self.squares.append(
            Utility(name=Square.Name.ELECTRIC_COMPANY,
                    property_set=self.get_property_set(PropertySet.UTILITY)))

        # Whitehall...
        self.squares.append(
            Street(name=Square.Name.WHITEHALL,
                   property_set=self.get_property_set(PropertySet.PURPLE),
                   price=140,
                   house_price=100,
                   rents=[10, 50, 150, 450, 625, 750]))

        # Northumberland Avenue...
        self.squares.append(
            Street(name=Square.Name.NORTHUMBERLAND_AVENUE,
                   property_set=self.get_property_set(PropertySet.PURPLE),
                   price=160,
                   house_price=100,
                   rents=[12, 60, 180, 500, 700, 900]))

        # Marylebone Station...
        self.squares.append(
            Station(name=Square.Name.MARYLEBONE_STATION,
                    property_set=self.get_property_set(PropertySet.STATION)))

        # Bow Street...
        self.squares.append(
            Street(name=Square.Name.BOW_STREET,
                   property_set=self.get_property_set(PropertySet.ORANGE),
                   price=180,
                   house_price=100,
                   rents=[14, 70, 200, 550, 750, 950]))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Marlborough Street...
        self.squares.append(
            Street(name=Square.Name.MARLBOROUGH_STREET,
                   property_set=self.get_property_set(PropertySet.ORANGE),
                   price=180,
                   house_price=100,
                   rents=[14, 70, 200, 550, 750, 950]))

        # Vine Street...
        self.squares.append(
            Street(name=Square.Name.VINE_STREET,
                   property_set=self.get_property_set(PropertySet.ORANGE),
                   price=200,
                   house_price=100,
                   rents=[16, 80, 220, 600, 800, 1000]))

        # Free Parking...
        self.squares.append(FreeParking())

        # Strand...
        self.squares.append(
            Street(name=Square.Name.STRAND,
                   property_set=self.get_property_set(PropertySet.RED),
                   price=220,
                   house_price=150,
                   rents=[18, 90, 250, 700, 875, 1050]))

        # Chance...
        self.squares.append(Chance())

        # Fleet Street...
        self.squares.append(
            Street(name=Square.Name.FLEET_STREET,
                   property_set=self.get_property_set(PropertySet.RED),
                   price=220,
                   house_price=150,
                   rents=[18, 90, 250, 700, 875, 1050]))

        # Trafalgar Square...
        self.squares.append(
            Street(name=Square.Name.TRAFALGAR_SQUARE,
                   property_set=self.get_property_set(PropertySet.RED),
                   price=240,
                   house_price=150,
                   rents=[20, 100, 300, 750, 925, 1100]))

        # Fenchurch Street Station...
        self.squares.append(
            Station(name=Square.Name.FENCHURCH_STREET_STATION,
                    property_set=self.get_property_set(PropertySet.STATION)))

        # Leicester Square...
        self.squares.append(
            Street(name=Square.Name.LEICESTER_SQUARE,
                   property_set=self.get_property_set(PropertySet.YELLOW),
                   price=260,
                   house_price=150,
                   rents=[22, 110, 330, 800, 975, 1150]))

        # Coventry Street...
        self.squares.append(
            Street(name=Square.Name.COVENTRY_STREET,
                   property_set=self.get_property_set(PropertySet.YELLOW),
                   price=260,
                   house_price=150,
                   rents=[22, 110, 330, 800, 975, 1150]))

        # Water Works...
        self.squares.append(
            Utility(name=Square.Name.WATER_WORKS,
                    property_set=self.get_property_set(PropertySet.UTILITY)))

        # Piccadilly...
        self.squares.append(
            Street(name=Square.Name.PICCADILLY,
                   property_set=self.get_property_set(PropertySet.YELLOW),
                   price=280,
                   house_price=150,
                   rents=[22, 120, 360, 850, 1025, 1200]))

        # Go To Jail...
        self.squares.append(GoToJailSquare())

        # Regent Street...
        self.squares.append(
            Street(name=Square.Name.REGENT_STREET,
                   property_set=self.get_property_set(PropertySet.GREEN),
                   price=300,
                   house_price=200,
                   rents=[26, 130, 390, 900, 1100, 1275]))

        # Oxford Street...
        self.squares.append(
            Street(name=Square.Name.OXFORD_STREET,
                   property_set=self.get_property_set(PropertySet.GREEN),
                   price=300,
                   house_price=200,
                   rents=[26, 130, 390, 900, 1100, 1275]))

        # Community Chest...
        self.squares.append(CommunityChest())

        # Bond Street...
        self.squares.append(
            Street(name=Square.Name.BOND_STREET,
                   property_set=self.get_property_set(PropertySet.GREEN),
                   price=320,
                   house_price=200,
                   rents=[28, 150, 450, 1000, 1200, 1400]))

        # Liverpool Street Station...
        self.squares.append(
            Station(name=Square.Name.LIVERPOOL_STREET_STATION,
                    property_set=self.get_property_set(PropertySet.STATION)))

        # Chance...
        self.squares.append(Chance())

        # Park Lane...
        self.squares.append(
            Street(name=Square.Name.PARK_LANE,
                   property_set=self.get_property_set(PropertySet.DARK_BLUE),
                   price=350,
                   house_price=200,
                   rents=[35, 175, 500, 1100, 1300, 1500]))

        # Super Tax...
        self.squares.append(Tax(name=Square.Name.SUPER_TAX, tax=100))

        # Mayfair...
        self.squares.append(
            Street(name=Square.Name.MAYFAIR,
                   property_set=self.get_property_set(PropertySet.DARK_BLUE),
                   price=400,
                   house_price=200,
                   rents=[50, 200, 600, 1400, 1700, 2000]))

    def _map_names_to_indexes(self):
        '''
        Maps the square names to their (zero-based) indexes on the board.

        Each name maps to a list of locations, as some square names (Chance
        and Community Chest) have multiple squares on the board.
        '''
        for index in range(len(self.squares)):
            name = self.squares[index].name
            if name not in self._name_to_index_map:
                self._name_to_index_map[name] = []
            self._name_to_index_map[name].append(index)

    def _setup_property_sets(self):
        '''
        Creates a property set for each set, and maps them to
        the set ID.
        '''
        def add_set(set_enum):
            self._property_set_map[set_enum] = PropertySet(set_enum)

        add_set(PropertySet.BROWN)
        add_set(PropertySet.LIGHT_BLUE)
        add_set(PropertySet.PURPLE)
        add_set(PropertySet.ORANGE)
        add_set(PropertySet.RED)
        add_set(PropertySet.YELLOW)
        add_set(PropertySet.GREEN)
        add_set(PropertySet.DARK_BLUE)
        add_set(PropertySet.STATION)
        add_set(PropertySet.UTILITY)



