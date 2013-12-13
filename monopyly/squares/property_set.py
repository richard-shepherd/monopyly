
class PropertySet(object):
    '''
    Holds the collection of properties in a set and includes
    helper functions related to the ownership of properties.
    '''

    # An 'enum' for the different property sets.
    BROWN = "Brown"
    LIGHT_BLUE = "Light blue"
    PURPLE = "Purple"
    ORANGE = "Orange"
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    DARK_BLUE = "Dark blue"
    STATION = "Station"
    UTILITY = "Utility"

    def __init__(self, set_enum):
        '''
        The 'constructor'.
        '''
        self.properties = []
        self.set_enum = set_enum


    def __repr__(self):
        '''
        Returns the string name of the set.
        '''
        return self.__str__()

    def __str__(self):
        '''
        Returns the string name of the set.
        '''
        return self.set_enum

    def add_property(self, property):
        '''
        Adds a property to the set.
        '''
        self.properties.append(property)

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
        if len(owners) == 1 and owners[0][1] == self.number_of_properties:
            return owners[0][0]
        else:
            return None

    @property
    def owners(self):
        '''
        Returns the collection of owners of the properties in the
        set, along with the number of properties and the fraction
        of the set they own.

        Returned as a list of tuples, like:
        [(player1, 1, 0.333), (player2, 2, 0.666)]
        '''
        owners = {p.owner for p in self.properties if p.owner is not None}
        owner_info = []
        for owner in owners:
            properties_owned = sum(1 for p in self.properties if p.owner is owner)
            owner_info.append((owner, properties_owned, properties_owned/self.number_of_properties))
        return owner_info

    @property
    def all_properties_are_unmortgaged(self):
        '''
        Returns True if all the properties in the set are unmortgaged,
        False if at least one is mortgaged.
        '''
        for property in self.properties:
            if property.is_mortgaged:
                return False
        return True

    def intersection(self, properties):
        '''
        Returns the set of common properties between the set
        passed in and the properties in this set.
        '''
        return set.intersection(set(self.properties), properties)

    @property
    def can_build_houses(self):
        '''
        True if you can build houses on this set.

        This is False if the set is the stations or utilities, or if
        the set already has hotels on all properties.
        '''
        # Is the set the stations or utilities?
        if (self.set_enum == PropertySet.STATION or self.set_enum == PropertySet.UTILITY):
            return False

        # Do all properties already have hotels?
        for property in self.properties:
            if property.number_of_houses < 5:
                return True

        return False

    @property
    def house_price(self):
        '''
        Returns the house price.
        '''
        if (self.set_enum == PropertySet.STATION or self.set_enum == PropertySet.UTILITY):
            return 0

        return self.properties[0].house_price

