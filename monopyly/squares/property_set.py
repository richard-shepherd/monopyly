
class PropertySet(object):
    '''
    Holds the collection of properties in a set and includes
    helper functions related to the ownership of properties.
    '''

    # An 'enum' for the different property sets.
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

    def __init__(self, set_enum):
        '''
        The 'constructor'.
        '''
        self.properties = []
        self.set_enum = set_enum

    @property
    def number_of_properties(self):
        '''
        Returns the number of properties in the set.
        '''
        return len(self.properties)

    @property
    def number_of_owned_properties(self):
        '''
        Returns the number of properties in the set which are owned.
        '''
        return sum(1 for p in self.properties if p.owner is not None)

    @property
    def owner(self):
        '''
        Returns the owner (a Player object) if all the properties
        in the set are owned by the same player, or None if there
        is no overall owner.
        '''
        owners = self.owners
        if len(owners) == 1:
            return owners[0][0]
        else:
            return None

    @property
    def owners(self):
        '''
        Returns the collection of owners of the properties in the
        set, along with the fraction of the set they own.

        Returned as a list of tuples, like:
        [(player1, 0.333), (player2, 0.666)]
        '''
        owners = {p.owner for p in self.properties if p.owner is not None}
        return [(o, sum(1 for p in self.properties if p.owner is o)/self.number_of_properties)
                for o in owners]

