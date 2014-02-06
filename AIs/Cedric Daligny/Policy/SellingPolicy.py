__author__ = 'Cedric'

from ..Memory import *
from monopyly import *

class SellingPolicy(object):
    def __init__(self, ai, memory):
        '''
        ctor
        '''
        self.ai = ai
        self.memory = memory

    def computeMortgage(self, game_state, player):
        '''
        Gives the player an option to mortgage properties.

        This is called before any debt is paid (house building, rent,
        tax, fines from cards etc).

        Notes:
        - You receive half the face value of each property mortgaged.

        - You cannot mortgage properties with houses on them.
          (The AI will have been given the option to sell houses before this
          function is called.)

        Return a list of properties to mortgage, for example:
        [bow_street, liverpool_street_station]

        The properties should be Property objects.

        Return an empty list if you do not want to mortgage anything.

        The default behaviour is not to mortgage anything.
        '''
        if self.ai.needed_money > 0:
            result = []
            money_from_mortgage = 0
            for property in player.state.properties:
                if type(property) != Street:
                    if property.is_mortgaged == False:
                        money_from_mortgage += property.price / 2
                        result.append(property)
                        if money_from_mortgage > self.ai.needed_money:
                            #Logger.log("SellingPolicy::mortgage case 1- mortgage value: " + format(money_from_mortgage) + " vs needed: " + format(self.ai.needed_money),Logger.WARNING)
                            return result
                else:
                    if property.is_mortgaged == False and property.number_of_houses == 0:
                        money_from_mortgage += property.price / 2
                        result.append(property)
                        if money_from_mortgage > self.ai.needed_money:
                            #Logger.log("SellingPolicy::mortgage case 2 - mortgage value: " + format(money_from_mortgage) + " vs needed: " + format(self.ai.needed_money),Logger.WARNING)
                            return result

            #Logger.log("SellingPolicy::mortgage case 3 - mortgage value: " + format(money_from_mortgage) + " vs needed: " + format(self.ai.needed_money),Logger.WARNING)
            return result
        return []

    def computeHouse(self, game_state, player):
        '''
        Gives the player the option to sell properties.

        This is called when any debt, fine or rent has to be paid. It is
        called just before mortgage_properties (below).

        Notes:
        - You cannot mortgage properties with houses on them, so if you
          plan to mortgage, make sure you sell all the houses first.

        - For each house sold you receive half the price that they were
          bought for.

        - Houses on a set must end up 'balanced', ie no property can have
          more than one more house than any other property in the set.

        Return a list of tuples of the streets and number of houses you
        want to sell. For example:
        [(old_kent_road, 1), (bow_street, 1)]

        The streets should be Property objects.

        The default is not to sell any houses.
        '''
        if self.ai.needed_money > 0:
            money_from_mortgage = 0
            for property in player.state.properties:
                if type(property) != Street:
                    if property.is_mortgaged == False:
                        money_from_mortgage += property.price / 2
                else:
                    if property.is_mortgaged == False and property.number_of_houses == 0:
                        money_from_mortgage += property.price / 2
            #Logger.log("SellingPolicy::sell_house - mortgage value: " + format(money_from_mortgage) + " vs needed: " + format(self.ai.needed_money),Logger.WARNING)
            if money_from_mortgage < self.ai.needed_money:
                still_needed = self.ai.needed_money - money_from_mortgage
                #Logger.log("SellingPolicy::sell_house BY ONE - still needed: " + format(still_needed),Logger.WARNING)
                result = []
                money_got_by_house = 0
                # try one on each
                for owned_set in player.state.owned_sets:
                    for street in owned_set.properties:
                        if type(street) == Street:
                            if street.number_of_houses > 0:
                                result.append((street,1))
                                still_needed -= street.house_price / 2
                                money_got_by_house += street.house_price / 2
                    if still_needed <= 0:
                        #Logger.log("SP: needed money left case 1: " + format(self.ai.needed_money) + " money expected from house: " + format(money_got_by_house),Logger.WARNING)
                        self.ai.needed_money -= money_got_by_house
                        self.display_list(player,result)
                        return result
                #reinit before trying selling max of houses
                result = []
                money_got_by_house = 0
                still_needed = self.ai.needed_money - money_from_mortgage
                #Logger.log("SellingPolicy::sell_house ALL - still needed: " + format(still_needed),Logger.WARNING)
                #try all
                for owned_set in player.state.owned_sets:
                    for street in owned_set.properties:
                        if type(street) == Street:
                            if street.number_of_houses > 0:
                                result.append((street,street.number_of_houses))
                                still_needed -= (street.house_price / 2) * street.number_of_houses
                                money_got_by_house += (street.house_price / 2) * street.number_of_houses
                    if still_needed <= 0:
                        #Logger.log("SP: needed money left case 2: " + format(self.ai.needed_money) + " money expected from house: " + format(money_got_by_house),Logger.WARNING)
                        self.ai.needed_money -= money_got_by_house
                        self.display_list(player,result)
                        return result
                # if we need really money, sell all
                result = []
                for street in player.state.properties:
                    if type(street) == Street:
                        if street.number_of_houses > 0:
                            result.append((street,street.number_of_houses))
                #Logger.log("SP: needed money left case 3: " + format(self.ai.needed_money) + " money expected from house: " + format(money_got_by_house),Logger.WARNING)
                self.ai.needed_money -= money_got_by_house
                self.display_list(player,result)
                return result
        #Logger.log("SP: needed money left case 5: " + format(self.ai.needed_money) + " money expected from house: 0",Logger.WARNING)
        return []

    def display_list(self,player,list):
        #Logger.log("SELLING HOUSE BEGIN for " + player.name,Logger.WARNING)
        #for property in player.state.properties:
        #    if type(property) == Street:
        #        Logger.log("    property: " + property.name + " - " + format(property.number_of_houses),Logger.WARNING)
        #Logger.log("List length: " + format(len(list)),Logger.WARNING)
        #for elem in list:
        #    Logger.log("    elem: " + elem[0].name + " - " + format(elem[1]),Logger.WARNING)
        #Logger.log("SELLING HOUSE END for " + player.name,Logger.WARNING)
        pass

    def propose_deal(self,game_state,player):
        '''
        Called to allow the player to propose a deal.

        You return a DealProposal object.

        If you do not want to make a deal, return None.

        If you want to make a deal, you provide this information:
        - The player number of the player you are proposing the deal to
        - A list of properties offered
        - A list of properties wanted
        - Maximum cash offered as part of the deal
        - Minimum cash wanted as part of the deal.

        Properties offered and properties wanted are passed as lists of
        Property objects.

        If you offer money as part of the deal, set the cash wanted to zero
        and vice versa.

        Note that the cash limits will not be shown to the proposed-to player.
        When the deal is offered to them, they set their own limits for accepting
        the deal without seeing your limits. If the limits are acceptable to both
        players, the deal will be done at the halfway point.

        For example, Player1 proposes:
          Propose to: Player2
          Properties offered: Mayfair
          Properties wanted: (none)
          Maximum cash offered: 0
          Minimum cash wanted: 500

        Player2 accepts with these limits:
          Maximum cash offered: 1000
          Minimum cash wanted: 0

        The deal will be done with Player2 receiving Mayfair and paying £750
        to Player1.

        The only 'negotiation' is in the managing of cash along with the deal
        as discussed above. There is no negotiation about which properties are
        part of the deal. If a deal is rejected because it does not contain the
        right properties, another deal can be made at another time with different
        lists of properties.

        Example construction and return of a DealProposal object:
            return DealProposal(
                propose_to_player_number=2,
                properties_offered=[vine_street, bow_street],
                properties_wanted=[park_lane],
                maximum_cash_offered=200)

        The default is for no deal to be proposed.
        '''
        return None
