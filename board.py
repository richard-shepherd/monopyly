from squares import *


class Board(object):
    '''
    Represents the board.

    Holds a collection of objects which each implement the
    (implicit) Square interface, as well as the collection
    of Chance and Community Chest cards.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''
        # We add the collection of squares to the board...
        self.squares = []

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
        self.squares.append(IncomeTax())

        # Kings Cross...
        self.squares.append(Station(name=Property.Name.KINGS_CROSS_STATION))

        # The Angel Islington...
        self.squares.append(
            Street(name=Property.Name.THE_ANGEL_ISLINGTON,
                   street_set=Property.Set.LIGHT_BLUE,
                   price=100,
                   house_price=50,
                   rents=Street.Rents(6, 30, 90, 270, 400, 550)))
