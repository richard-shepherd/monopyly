__author__ = 'Cedric'

from monopyly import *

'''
    buying_house_policy                     # ONE_COMPLETE_SET, ONE_AVAILABLE_PROPERTY, ALL_AVAILABLE_PROPERTY, ALL_COMPLETE_SET
    buying_house_repartition_policy         # MAXIMIZE_HOTEL, SAME_SIZE
    # information used to know if house will be build
    buying_house_cash_threshold             # similar to the property cash threshold, the remaining cash wanted  after transaction occurs
    buying_house_sorter                     # value use to sort the property in terms of house building preferences (-1 means that housing is not available)
'''
class HousePolicy_v2(object):
    class HousePolicy(object):
        ONE_COMPLETE_SET = 0
        ONE_AVAILABLE_PROPERTY = 1
        ALL_AVAILABLE_PROPERTY = 2
        ALL_COMPLETE_SET = 3

    class RepartitionPolicy(object):
        MAXIMIZE_HOTEL = 0
        SAME_SIZE = 1

    def __init__(self,ai,policy,repartition):
        self.ai = ai
        self.policy = policy
        self.repartition = repartition

    def compute(self,game_state, player):
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
        set_available_to_build = []
        for owned_set in player.state.owned_unmortgaged_sets:
            # We can't build on stations or utilities, or if the
            # set already has hotels on all the properties...
            if not owned_set.can_build_houses:
                continue
            set_available_to_build.append(owned_set)

        if len(set_available_to_build) > 0:
            if self.repartition == self.RepartitionPolicy.MAXIMIZE_HOTEL:
                best_set = set_available_to_build[0]
                for set in set_available_to_build:
                    property = set.properties[len(set.properties) - 1]
                    best_property = best_set.properties[len(best_set.properties) - 1]
                    if self.ai.properties_information[property.name][5] > self.ai.properties_information[best_property.name][5]:
                        best_set = set

                if self.policy == self.HousePolicy.ONE_COMPLETE_SET:
                    cost = best_set.house_price * best_set.number_of_properties
                    if (player.state.cash - cost) >= self.ai.properties_information[best_set.properties[0].name][4]:
                        # We build one house on each property...
                        result = [(p, 1) for p in best_set.properties]
                        self.display_list(player,result)
                        return result
                elif self.policy == self.HousePolicy.ONE_AVAILABLE_PROPERTY:
                    valid_property = best_set.properties[len(best_set.properties) - 1]
                    nb_house = valid_property.number_of_houses
                    for property in best_set.properties:
                        if property.number_of_houses < nb_house:
                            valid_property = property
                            nb_house = valid_property.number_of_houses
                    if (player.state.cash - best_set.house_price) >= self.ai.properties_information[valid_property.name][4]:
                        # We build one house on property...
                        result = [(valid_property, 1)]
                        self.display_list(player,result)
                        return result
            elif self.repartition == self.RepartitionPolicy.SAME_SIZE:
                max_size = 0
                for property in player.state.properties:
                    if type(property) == Street:
                        if property.number_of_houses > max_size:
                            max_size = property.number_of_houses

                best_set = set_available_to_build[0]
                for set in set_available_to_build:
                    property = set.properties[len(set.properties) - 1]
                    best_property = best_set.properties[len(best_set.properties) - 1]
                    if self.ai.properties_information[property.name][5] > self.ai.properties_information[best_property.name][5] and best_property.number_of_houses <= max_size:
                        best_set = set

                if self.policy == self.HousePolicy.ONE_COMPLETE_SET:
                    cost = best_set.house_price * best_set.number_of_properties
                    if (player.state.cash - cost) >= self.ai.properties_information[best_set.properties[0].name][4]:
                        # We build one house on each property...
                        result = [(p, 1) for p in best_set.properties]
                        self.display_list(player,result)
                        return result
                elif self.policy == self.HousePolicy.ONE_AVAILABLE_PROPERTY:
                    valid_property = best_set.properties[len(best_set.properties) - 1]
                    nb_house = valid_property.number_of_houses
                    for property in best_set.properties:
                        if property.number_of_houses < nb_house:
                            valid_property = property
                            nb_house = valid_property.number_of_houses
                    if (player.state.cash - best_set.house_price) >= self.ai.properties_information[valid_property.name][4]:
                        # We build one house on property...
                        result = [(valid_property, 1)]
                        self.display_list(player,result)
                        return result
        return []

    def display_list(self,player,list):
        #Logger.log("BUYING HOUSE BEGIN for " + player.name,Logger.WARNING)
        #for property in player.state.properties:
        #    if type(property) == Street:
        #        Logger.log("    property: " + property.name + " - " + format(property.number_of_houses),Logger.WARNING)
        #Logger.log("List length: " + format(len(list)),Logger.WARNING)
        #for elem in list:
        #    Logger.log("    elem: " + elem[0].name + " - " + format(elem[1]),Logger.WARNING)
        #Logger.log("BUYING HOUSE END for " + player.name,Logger.WARNING)
        pass

