__author__ = 'James'
from monopyly import *
from .property_probs_calcs import PropertyProbCalcs
from .property_sim import *
from .board_utils import *

class DecisionUtils():
    def __init__(self, property_probs):
        self.property_probs = property_probs
        self.board_utils = BoardUtils(self.property_probs)
        self.multiplier_max_price = 2
        self.multiplier_50_perc_owned = 2
        self.multiplier_50_perc_owned_by_one_other = 1.5
        self.multiplier_own_one_other_available = 1.5
        self.multiplier_station = 1.5
        self.multiplier_first_property_in_set = 1.25
        #How worried I am that others own properties and I don't
        self.multiplier_worry = 1
        self.turns_ive_had_in_game=0

    def percentage_of_sets_player_owns_to_average_num_others_own(self, game_state, player):
        #Workout the number of sets I own
        #The number of sets others own on average
        #What percentage above the average do I have?
        owned_sets = game_state.board.get_owned_sets(True)
        all_players = game_state.players
        total_owned_by_me = 0
        total_owned_by_all_others = 0
        average_owned_by_others=0
        for k in owned_sets.keys():
            if player.is_same_player(k) :
                total_owned_by_me = len(owned_sets[k])
            else:
                total_owned_by_all_others = total_owned_by_all_others + len(owned_sets[k])
        average_owned_by_others = total_owned_by_all_others / (len(all_players) - 1)
        if average_owned_by_others > 0:
            percentage_greater_i_own = 100 * ((total_owned_by_me - average_owned_by_others) / average_owned_by_others)
        else:
            percentage_greater_i_own = 100
        return percentage_greater_i_own

    def number_of_monopolies_player_would_get(self,property_list_they_would_get,player):
        #Returns the NUMBER of monopolies a player would get IF they got all these proposed properties
        total_monopolies_player_would_get=0
        sets_already_checked=[]
        for prop in property_list_they_would_get:
            #Check if it would give me a monopoly
            gives_a_monopoly_flag=True
            if (not prop.property_set in sets_already_checked and not(prop.property_set.set_enum == PropertySet.UTILITY
                    or prop.property_set.set_enum ==PropertySet.STATION)):
                for other_prop_in_set in prop.property_set.properties:
                    #Loop through all the properties in the set
                    #If Except for the properties in question, they would get a set
                    #then say that this would give them a monopoly
                    if other_prop_in_set in property_list_they_would_get:
                        #The property in this set is in the list of the proposed - still a chance for them to
                        #get a monopoly
                        pass
                    else:
                        if player.is_same_player(other_prop_in_set.owner):
                            #the property in this set has the same owner - not looking good
                            pass
                        else:
                            #There's a different owner, all fine
                            gives_a_monopoly_flag=False
                            break

                if gives_a_monopoly_flag == True:
                    total_monopolies_player_would_get=total_monopolies_player_would_get + 1
            sets_already_checked.append(prop.property_set)
        return total_monopolies_player_would_get

    def amount_property_is_worth_to_a_player(self, game_state, property, player):
        #Decide how much a property is worth
        #TODO: How to split the amounts to offer AND how much to cap them by?
        #TODO: Could we look at other player's cash amounts to judge how much to offer?
        #property_price=property.price
        #property_price=0

        #percentage_greater_player_owns_to_others=self.percentage_of_sets_player_owns_to_average_num_others_own(game_state,player)
        worry_multiplier=1
        if isinstance(property,Street):
            avg_expected_return_1_turn=self.property_probs.income_per_turn(property.name,num_houses=3, set_owned=True,
                                                                number_of_stations_owned=None)
        elif isinstance(property,Station):
            avg_expected_return_1_turn=self.property_probs.income_per_turn(property.name,num_houses=None, set_owned=True,
                                                                number_of_stations_owned=2)
        else:
            #For a utility
            avg_expected_return_1_turn=1
        #Assume 25 turns per game - after this we won't have long enough to get any money - so property is worth it's
        #face value
        if self.turns_ive_had_in_game <40:
            avg_expected_return_remaining_turns=avg_expected_return_1_turn * (40-self.turns_ive_had_in_game)
        else:
            avg_expected_return_remaining_turns=0
        amount_property_is_worth=avg_expected_return_remaining_turns
        '''
        if percentage_greater_player_owns_to_others < 0:
            worry_multiplier = - percentage_greater_player_owns_to_others * self.multiplier_worry

        percentage_of_set_player_owns = self.board_utils.percentage_of_property_set_owned_by_player(game_state.board, player, property.property_set)
        percentage_of_set_still_available = self.board_utils.percentage_of_property_set_owned_by_player(game_state.board, None, property.property_set)
        if percentage_of_set_player_owns >= 50:
            #If we have 50% or MORE of properties in this set - then we can offer a lot
            amount_property_is_worth = avg_expected_return_remaining_turns + (worry_multiplier *
                                                                                  self.multiplier_50_perc_owned
                                                                                  * property_price)
        elif self.board_utils.max_percentage_of_property_owned_by_single_player(game_state, property.property_set) >= 50:
            #If someone else has 50% or more of properties in a set then we can offer a lot
            #to block their progress
            amount_property_is_worth = avg_expected_return_remaining_turns+(worry_multiplier
                                           * self.multiplier_50_perc_owned_by_one_other
                                           * property_price)
        elif percentage_of_set_player_owns > 0 and percentage_of_set_still_available > 0:
            #If we have some properties in the set and others are still available we can offer a reasonable amount
            #TODO: What amount to offer for "reasonable"?
            #Offer 3/4 of our maximum price for this property
            amount_property_is_worth = avg_expected_return_remaining_turns+(worry_multiplier *
                                                                                self.multiplier_own_one_other_available
                                                                                * property_price)
        elif self.board_utils.is_station(property.name):
            #If it is a station then we can offer a reasonable amount
            amount_property_is_worth = avg_expected_return_remaining_turns+(worry_multiplier
                                                                            * self.multiplier_station * property_price)
        elif percentage_of_set_still_available == 100:
            #First property available in a set
            amount_property_is_worth = avg_expected_return_remaining_turns+(worry_multiplier
                                                                            * self.multiplier_first_property_in_set
                                                                            * property_price)
        else:
            #If it is a utility or anything else then we offer face value
            amount_property_is_worth = property_price+ avg_expected_return_remaining_turns
        '''
        #Make sure we return an integer amount
        return int(max(amount_property_is_worth,property.price))

    def best_house_to_sell(self, sim_property_list):
        # returns the best house to sell as a property name
        # expects a list of properties that ARE streets with houses
        prob_calc=PropertyProbCalcs()

        #TODO: check this a  good strategy
        #Sell the house that gives the LEAST lost income
        #Could also be least lost income PER cost of house
        #Could also consider the amount of money we're trying to raise
        #That gets difficult though,and needs to be considered as part
        #of a larger group of decisions as to which MULTIPLE
        #player actions is the best route

        #Current problem is that we test all these different properties - and the number of houses removed - STAYS removed
        #If it's NOT the best property we need to replace the houses
        best_property = None
        min_income_found=9999
        for sim_property in sim_property_list:
            current_test_income_loss = 99999
            if sim_property.sim_number_of_houses > 0:
                if self.adding_house_leaves_set_balanced(sim_property , sim_property_list, -1):
                    current_test_income_loss=prob_calc.income_per_turn(sim_property.name,sim_property.sim_number_of_houses, True )
                    if current_test_income_loss< min_income_found:
                        min_income_found = current_test_income_loss
                        best_property=sim_property

        return best_property


    def adding_house_leaves_set_balanced (self, sim_property_with_house_to_add,sim_properties, number_of_houses_to_add):

        #Assume the list passed in contains ALL the properties in a set PLUS some extra ones
        #The aim is to add/subtract one for houses on a property - and see if the set still balances
        #If it DOESN'T balance we replace/remove the house

        #Create a list of properties in this set
        property_sim_set=[]
        for prop in sim_properties:
            if prop.property_set == sim_property_with_house_to_add.property_set:
                if prop.name == sim_property_with_house_to_add.name:
                    prop.sim_number_of_houses = prop.sim_number_of_houses + number_of_houses_to_add
                property_sim_set.append(prop)
        #Add the specified number of houses to the correct property

        houses_for_each_property = [p.sim_number_of_houses for p in property_sim_set]
        if max(houses_for_each_property) <= 5 and (max(houses_for_each_property) - min(houses_for_each_property)) <= 1:
            #Always replace the house
            sim_property_with_house_to_add.sim_number_of_houses = sim_property_with_house_to_add.sim_number_of_houses - number_of_houses_to_add
            return True
        else:
            #Always replace the house
            sim_property_with_house_to_add.sim_number_of_houses = sim_property_with_house_to_add.sim_number_of_houses - number_of_houses_to_add
            return False
    
    def improve_properties(self, owned_sim_properties , spare_cash):
        #Loop through all properties i own where i can build
        #and add a house on the one with maximum expected income
        #TODO:Could also build on the place that is quickest
        #to recoup accumulated cost
        #TODO:Could also build according to where
        #players are on the board AND who we want to victimise
        prob_calc=PropertyProbCalcs()
        remaining_spare_cash = spare_cash
        max_income_found=-9999
        found_prop_to_improve = True
        while found_prop_to_improve:
            found_prop_to_improve = False
            for sim_property in owned_sim_properties :
                current_test_income_gain = -99999
                if sim_property.sim_number_of_houses < 5 and sim_property.property_set.house_price <= remaining_spare_cash:  
                    if self.adding_house_leaves_set_balanced(sim_property , owned_sim_properties, 1):

                        current_test_income_gain=prob_calc.income_per_turn(sim_property.name,sim_property.sim_number_of_houses, True )
                        if current_test_income_gain > max_income_found:
                            found_prop_to_improve = True
                            max_income_found = current_test_income_gain
                            best_property = sim_property
            if found_prop_to_improve:
                remaining_spare_cash -= best_property.property_set.house_price
                best_property.sim_number_of_houses = best_property.sim_number_of_houses + 1
        return owned_sim_properties


    def best_property_to_mortgage(self, game_state, my_own_player, sim_property_set_for_mortgage_calcs):
        #Find the best property to mortgage. This is one with lowest lost of expected income
        #TODO: Could also be those with highest number of rolls before mortgage value is lost
        min_income_loss=9999
        best_property=None
        for prop in sim_property_set_for_mortgage_calcs:
            set_owned = (prop.property_set.owner == my_own_player)
            if prop.is_mortgaged == False:
                if set_owned and prop.property_set in [p.property_set for p in self.board_utils.get_properties_i_own_with_houses(game_state.board, my_own_player)]:
                    #This property or one of the set has houses - can't be mortgaged
                    pass
                else:
                    if self.board_utils.is_utility(prop.name):
                        #Always mortgage a utility
                        return prop
                    if self.board_utils.is_station(prop.name):

                        current_income_loss = self.property_probs.income_per_turn(prop.name, None, None, self.board_utils.number_of_stations_owned(
                                game_state.board, my_own_player))
                    else:
                        current_income_loss = self.property_probs.income_per_turn(prop.name, 0, set_owned)
                    if min_income_loss > current_income_loss:
                        min_income_loss = current_income_loss
                        best_property = prop
        return best_property

    def best_property_to_unmortgage(self, game_state, my_own_player, sim_property_set_for_mortgage_calcs):
        #Find the best property to unmortgage. This is one with lowest lost of expected income
        #TODO: Could also be those with lowest number of rolls before mortgage value is lost
        max_income_loss=-9999
        best_property=None
        for prop in sim_property_set_for_mortgage_calcs:
            set_owned = (prop.property_set.owner == my_own_player)
            if prop.is_mortgaged == True:
                if self.board_utils.is_utility(prop.name):
                    #Never unmortgage a utility
                    #TODO: Unless it's the ONLY mortgaged property
                    continue

                if self.board_utils.is_station(prop.name):
                    current_income_gain = self.property_probs.income_per_turn(prop.name, None, None, self.board_utils.number_of_stations_owned(
                            game_state.board, my_own_player))
                else:
                    current_income_gain = self.property_probs.income_per_turn(prop.name, 0, set_owned)
                if max_income_loss < current_income_gain:
                    max_income_loss = current_income_gain
                    best_property = prop


        return best_property




