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
            Street(name="Old Kent Road",
                   street_set=Property.Set.BROWN,
                   price=60,
                   house_price=50,
                   rents=Street.Rents(2, 10, 30, 90, 160, 250)))

        # Community Chest...
        self.squares.append(CommunityChest())

