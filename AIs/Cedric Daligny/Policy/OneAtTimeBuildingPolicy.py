__author__ = 'Cedric'

from .HousingPolicy import HousingPolicy

class OneAtTimeBuildingPolicy(HousingPolicy):
    def __init__(self):
        '''
        ctor
        '''

    def compute(self, game_state, player):
        set = None
        street_min_house = 16 # 3 streets with 5 houses + 1

        # find the set with the min of house
        for owned_set in player.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                continue

            set_houses_size = 0
            set_house_price = 0
            for street in owned_set.properties:
                set_houses_size += street.number_of_houses
                set_house_price += street.house_price

            if set_houses_size < street_min_house and set_house_price < player.state.cash:
                set = owned_set

        if set != None:
            # We build one house on each property...
            return [(p, 1) for p in set.properties]

        # We can't build...
        return []
