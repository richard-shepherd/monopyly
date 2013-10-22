import copy


class Square(object):
    '''
    A base class for squares on the Monopoly board.
    '''
    class Name(object):
        '''
        An 'enum' for the squares on the board.
        '''

        # The "enum"...
        GO = "Go"
        OLD_KENT_ROAD = "Old Kent Road"
        COMMUNITY_CHEST = "Community Chest"
        WHITECHAPEL_ROAD = "Whitechapel Road"
        INCOME_TAX = "Income Tax"
        KINGS_CROSS_STATION = "Kings Cross Station"
        THE_ANGEL_ISLINGTON = "The Angel Islington"
        CHANCE = "Chance"
        EUSTON_ROAD = "Euston Road"
        PENTONVILLE_ROAD = "Pentonville Road"
        JAIL = "Jail"
        PALL_MALL = "Pall Mall"
        ELECTRIC_COMPANY = "Electric Company"
        WHITEHALL = "Whitehall"
        NORTHUMBERLAND_AVENUE = "Northumberland Avenue"
        MARYLEBONE_STATION = "Marylebone Station"
        BOW_STREET = "Bow Street"
        MARLBOROUGH_STREET = "Marlborough Street"
        VINE_STREET = "Vine Street"
        FREE_PARKING = "Free Parking"
        STRAND = "Strand"
        FLEET_STREET = "Fleet Street"
        TRAFALGAR_SQUARE = "Trafalgar Square"
        FENCHURCH_STREET_STATION = "Fenchurch Street Station"
        LEICESTER_SQUARE = "Leicester Square"
        COVENTRY_STREET = "Coventry Street"
        WATER_WORKS = "Water Works"
        PICCADILLY = "Piccadilly"
        GO_TO_JAIL = "Go To Jail"
        REGENT_STREET = "Regent Street"
        OXFORD_STREET = "Oxford Street"
        BOND_STREET = "Bond Street"
        LIVERPOOL_STREET_STATION = "Liverpool Street Station"
        PARK_LANE = "Park Lane"
        SUPER_TAX = "Super Tax"
        MAYFAIR = "Mayfair"

    def __init__(self, name):
        '''
        The 'constructor'.
        '''
        self.name = name

    def copy(self):
        '''
        Returns a copy of the square.

        Can be overridden in derived classes, if necessary, to
        provide more efficient copying.
        '''
        return copy.deepcopy(self)
