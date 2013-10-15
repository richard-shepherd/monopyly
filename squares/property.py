
class Property(object):
    '''
    A base class for properties, which manages some common features
    of them.

    This include holding whether the property is owned (and if so, who by)
    and whether the property is mortgaged.

    Derived classes are: Street, Station, Utility.
    '''

    class Set(object):
        '''
        An 'enum' for the different property sets.
        '''
        INVALID = 0
        BROWN = 1
        LIGHT_BLUE = 2
        PURPLE = 3
        ORANGE = 4
        RED = 5
        YELLOW = 6
        GREEN = 7
        DARK_BLUE = 8
        STATION = 9
        UTILITY = 10

    class Names(object):
        '''
        Enums and string names for the various properties.
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
        PICADILLY = "Picadilly"
        GO_TO_JAIL = "Go To Jail"
        REGENT_STREET = "Regent Street"
        OXFORD_STREET = "Oxford Street"
        BOND_STREET = "Bond Street"
        LIVERPOOL_STREET_STATION = "Liverpool Street Station"
        PARK_LANE = "Park Lane"
        SUPER_TAX = "Super Tax"
        MAYFAIR = "Mayfair"


    def __init__(self, name, street_set, price):
        '''
        The 'constructor'.
        '''
        self.name = name
        self.street_set = street_set
        self.price = price
        self.mortgaged = False
        self.owner = None




