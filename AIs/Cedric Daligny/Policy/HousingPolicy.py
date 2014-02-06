__author__ = 'Cedric'

#from monopyly import *

class HousingPolicy(object):
    def __init__(self):
        '''
        ctor
        '''

    def compute(self, game_state, player):
        '''
        Called near the start of the player's turn to give the option of building houses.

        Return a list of tuples indicating which properties you want to build houses
        on and how many houses to build on each. For example:
        [(park_lane, 3), (mayfair, 4)]

        The properties should be Property objects.

        Return an empty list if you do not want to build.

        Notes:
        - You must own a whole set of unmortgaged properties before you can
          build houses on it.

        - You can build on multiple sets in one turn. Just specify all the streets
          and houses you want to build.

        - Build five houses on a property to have a "hotel".

        - You specify the _additional_ houses you will be building, not the
          total after building. For example, if Park Lane already has 3 houses
          and you specify (park_lane, 2) you will end up with 5
          houses (ie, a hotel).

        - Sets must end up with 'balanced' housing. No square in a set can
          have more than one more house than any other. If you request an
          unbalanced build, the whole transaction will be rolled back, even
          if it includes balanced building on other sets as well.

        - If you do not have (or cannot raise) enough money to build all the
          houses specified, the whole transaction will be rolled back. Between
          this function call and money being taken, you will have an opportunity
          to mortgage properties or make deals.

        The default behaviour is not to build.
        '''

        # We find the first set we own that we can build on...
        for owned_set in player.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                continue

            # We see how much money we need for one house on each property...
            cost = owned_set.house_price * owned_set.number_of_properties
            if player.state.cash > cost:
                # We build one house on each property...
                return [(p, 1) for p in owned_set.properties]

        # We can't build...
        return []
