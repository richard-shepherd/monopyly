from monopyly import *
from random import *
from .board_utils import *
from .decision_utils import *
from .property_probs_calcs import PropertyProbCalcs

class JamesTyasBasicsAI(PlayerAIBase):
    '''
    This AI counts its number of turns in a game

    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.total_games = 0
        self.total_turns = 0
        self.panic_selling = 0
        self.turn_amount_owed = 0
        self.property_probs=PropertyProbCalcs()
        self.board_utils=BoardUtils(self.property_probs)
        self.decision_utils=DecisionUtils(self.property_probs)
        self.turndealcount=0


    def start_of_game(self):
        #Called for all players
        self.panic_selling = 0
        self.number_mortgaged_properties = 0
        self.turn_amount_owed = 0
        self.decision_utils.turns_ive_had_in_game = 0
        #print("Average turns per game after " + str(self.total_games) + " is " \
              #+ str(self.total_turns/self.total_games))
        self.total_games += 1
        self.properties_with_triple_rejection=[]
        self.properties_tried_cash_only=[]
        self.properties_with_double_rejection=[]


    def start_of_turn(self, game_state, player):
        #NB called for all players so need to check if I am this player
        #List all properties I own
        self.turn_amount_owed = 0
        self.panic_selling = 0
        self.house_and_build_instructions_saved=None
        self.turndealcount=0
        self.deal_turn_count=0
        self.cash_buffer_required_saved=-999
        #Save game_state in case it is needed for the Jail calculation
        self.current_game_state=game_state
        if player.is_same_player(self):
            # all_props = ''
            # for current_property in self.board_utils.get_properties_i_own(game_state.board, player):
            #     all_props = all_props + ', ' + current_property.name
            # if all_props != '':
            #     print(all_props)
            self.decision_utils.turns_ive_had_in_game += 1
            self.total_turns += 1

    def get_out_of_jail(self, game_state, player):
        #TODO define jail strategy
        if self.decision_utils.percentage_of_sets_player_owns_to_average_num_others_own(game_state,player)>0:
            #I own more set than others - stay in Jail
            return PlayerAIBase.Action.STAY_IN_JAIL
        if (player.state.number_of_get_out_of_jail_free_cards >= 1):
            return PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        else:
            if(player.state.cash - self.cash_buffer_required(game_state,player)>= 50):
                return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL

        return PlayerAIBase.Action.STAY_IN_JAIL

    def get_name(self):
        '''
        Returns this AI's name.
        '''
        return "ProbopolyNot"

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        #Always take chance
        return PlayerAIBase.Action.TAKE_A_CHANCE


    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property.
        '''
        #Buy all the stations
        if (self.board_utils.is_station(property.name)  and player.state.cash > property.price):
            return PlayerAIBase.Action.BUY
      #  if property.name not in self.properties_we_like:
       #     return

        # We want to buy the property, but do we have enough money?
        if (player.state.cash - self.cash_buffer_required(game_state,player))> property.price:
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY
        #else:

    def money_will_be_taken(self, player, amount):
        # Check to see if we've got enough money
        self.turn_amount_owed=amount
        if (player.state.cash>=amount):
            # No need to allow panic selling
            self.panic_selling = 0

            pass
        else:
            #Allow panic_selling to avoid going bankrupt
            self.panic_selling = 1


    def money_taken(self, player, amount):
        # Paid our debt - set amount owed back to zero and not panic selling
        self.turn_amount_owed = 0
        self.panic_selling = 0

    def sell_houses(self, game_state, player):
        if(self.panic_selling == 1):
            total_income_from_house_sales = 0
            #TODO Check first if there's a better option that can be done later (e.g. mortgage a property)
            sim_property_set_for_mortgage_calcs = SimPropertySet(self.board_utils.get_properties_i_own(game_state.board, player)).sim_properties
            max_cash_from_mortgaging = self.max_cash_obtained_by_mortgaging_properties(game_state, player, sim_property_set_for_mortgage_calcs)
            if  max_cash_from_mortgaging + player.state.cash > self.turn_amount_owed:
                #No need to sell houses
                return []

            property_and_house_to_sell_list=[]
            remaining_properties_with_houses=[]
            properties_with_houses = self.board_utils.get_properties_i_own_with_houses(game_state.board, player)
            for prop_with_house in properties_with_houses:
                remaining_properties_with_houses.append(SimProperty(prop_with_house))
            if remaining_properties_with_houses is not None:
                while player.state.cash + max_cash_from_mortgaging + total_income_from_house_sales < self.turn_amount_owed:

                    #enough if we mortgaged now

                    #Work out if any of these properties have any remaining houses on them
                    found_a_house = False
                    for sim_prop_check_house in remaining_properties_with_houses:
                        if sim_prop_check_house.sim_number_of_houses>0:
                            found_a_house = True
                            break
                    if found_a_house == False:
                        break

                    property_with_house_to_sell = self.decision_utils.best_house_to_sell(remaining_properties_with_houses)
                    if not property_with_house_to_sell is None:
                        #After house sale - retest the mortgaging income to see if we'd have
                        for current_prop in sim_property_set_for_mortgage_calcs:
                            if current_prop.name == property_with_house_to_sell:
                                current_prop.sim_number_of_houses = current_prop.sim_number_of_houses - 1
                        max_cash_from_mortgaging=self.max_cash_obtained_by_mortgaging_properties(game_state, player, sim_property_set_for_mortgage_calcs)
                        remaining_properties_with_houses = self.board_utils.remove_house_from_property_in_list(property_with_house_to_sell,remaining_properties_with_houses)
                        total_income_from_house_sales = total_income_from_house_sales + property_with_house_to_sell.property_set.house_price/2
                    else:
                        break
                #Loop through properties to sell - generating a list
                for sim_property in remaining_properties_with_houses:
                    if sim_property.sim_number_of_houses < sim_property.number_of_houses:
                        property_and_house_to_sell_list.append([sim_property.original_property,sim_property.number_of_houses -
                                                                                      sim_property.sim_number_of_houses])
                if (player.state.cash + total_income_from_house_sales > self.turn_amount_owed):
                    #Panic Over
                    self.panic_selling = 0

                if len(property_and_house_to_sell_list) >0:
                    return property_and_house_to_sell_list
        return []


    def players_birthday(self):
    #Pay 10 fee instead of 100
        return "Happy Birthday!"




    def build_houses(self, game_state, player):

        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)
        return house_building_instructions_and_cost.get(1)

    def house_building_instructions_and_cost(self,game_state, player):
    # If we have spare cash ABOVE the cash buffer then spend on houses
        #Has this already been calculated for this turn?
        if not self.house_and_build_instructions_saved is None:
            return self.house_and_build_instructions_saved
        #TODO: How much cash to keep for buying properties and making deals?
        total_improvement_cost=0
        build_instructions =[]
        props_to_improve = []
        spare_cash = player.state.cash - self.cash_buffer_required(game_state, player)
        if spare_cash > 0:
            #TODO: Work out best place to build houses,1 by 1
            #then continue until all spare cash has been spent
            owned_sim_properties=[]
            for prop_set in player.state.owned_unmortgaged_sets:
                if prop_set.can_build_houses:
                    for prop in prop_set.properties:
                        owned_sim_properties.append(SimProperty(prop))
            if len(owned_sim_properties) > 0:
                props_to_improve = self.decision_utils.improve_properties(owned_sim_properties , spare_cash)

            properties_with_houses = self.board_utils.get_streets_i_own(game_state.board, player)
            if len(props_to_improve) > 0:
                for improved_prop in props_to_improve:
                    for prop in properties_with_houses:
                        if prop.name == improved_prop.name and prop.number_of_houses < improved_prop.sim_number_of_houses:
                            build_instructions.append((improved_prop.original_property,
                                                       improved_prop.sim_number_of_houses - prop.number_of_houses))
                            #Add up the cost too
                            total_improvement_cost=total_improvement_cost+(prop.property_set.house_price *(
                                improved_prop.sim_number_of_houses - prop.number_of_houses))
            #TODO:Work out best places to build houses for the maximum
            #return on investment as a SERIES of actions
        self.house_and_build_instructions_saved ={1:build_instructions, 2:total_improvement_cost}
        return self.house_and_build_instructions_saved

    def cash_buffer_required(self, game_state, my_own_player):
        # How much cash should we spare to pay fines etc.?
        if not self.cash_buffer_required_saved==-999:
            return self.cash_buffer_required_saved
       # expected_loss_per_roll = self.board_utils.get_total_expected_loss_per_roll_all_players(game_state.board,
        #    my_own_player)/(game_state.number_of_players - len(game_state.bankrupt_players) - 1)
        
        # Expected loss per owned square divided by number of players
        # less one
        #TODO: Look at maximum possible loss coming up within 1,2,3,4...
        #rolls of dice
        max_loss_single_roll = self.board_utils.max_loss_single_roll(game_state, my_own_player)

        #TODO: Experiment with risk - including available cash from mortgaging properties and selling houses
        self.cash_buffer_required_saved=max_loss_single_roll
        return self.cash_buffer_required_saved

    def unmortgage_properties(self, game_state, player):
        # Order of events is: make deals, unmortgage properties, build houses
        # Do we prefer to build houses or unmortgage?
        if self.number_mortgaged_properties == 0:
            #No properties to unmortgage
            return []
        cost_for_house_improvements=self.house_building_instructions_and_cost(game_state, player).get(2)
        available_cash_for_unmortgaging=player.state.cash - self.cash_buffer_required(game_state,player) - cost_for_house_improvements
        if available_cash_for_unmortgaging <0:
            #Not enough money to unmortgage
            return []
        cost_to_unmortgage = 0
        list_of_properties_to_unmortgage=[]
        sim_property_set_for_mortgage_calcs = SimPropertySet(self.board_utils.get_properties_i_own(game_state.board, player)).sim_properties

        found_a_prop_to_unmortgage = True
        if sim_property_set_for_mortgage_calcs is None or len(sim_property_set_for_mortgage_calcs)==0:
            return []

        while (found_a_prop_to_unmortgage and available_cash_for_unmortgaging - cost_to_unmortgage) > 0:
            found_a_prop_to_unmortgage = False
            prop_to_unmortgage = self.decision_utils.best_property_to_unmortgage(game_state, player,
                                                                                 sim_property_set_for_mortgage_calcs)
            if not prop_to_unmortgage is None:
                list_of_properties_to_unmortgage.append(prop_to_unmortgage.original_property)
                cost_to_unmortgage = cost_to_unmortgage + int(prop_to_unmortgage.price * 0.55)
                if cost_to_unmortgage > available_cash_for_unmortgaging:
                    #The best property to unmortgage cost TOO much
                    #Continue calculating BUT don't include it in the final decision
                     list_of_properties_to_unmortgage.remove(prop_to_unmortgage.original_property)
                     cost_to_unmortgage = cost_to_unmortgage - int(prop_to_unmortgage.price * 0.55)

                found_a_prop_to_mortgage = True
                sim_property_set_for_mortgage_calcs.remove(prop_to_unmortgage)
        if not(list_of_properties_to_unmortgage is None) or len(list_of_properties_to_unmortgage)>0:
            self.number_mortgaged_properties = self.number_mortgaged_properties - len(list_of_properties_to_unmortgage)
        return list_of_properties_to_unmortgage



    def mortgage_properties(self, game_state, player):
        '''
        - You cannot mortgage properties with houses on them.
          (The AI will have been given the option to sell houses before this
          function is called.)

        Return a list of properties to mortgage, for example:
        [bow_street, liverpool_street_station]
        '''
        list_of_properties_to_mortgage=[]
        if self.panic_selling == 1:
            #We need to get some cash
            #Mortgage properties until we have enough
            money_from_mortgages = 0
            sim_property_set_for_mortgage_calcs = SimPropertySet(self.board_utils.get_properties_i_own(game_state.board, player)).sim_properties

            found_a_prop_to_mortgage = True
            while found_a_prop_to_mortgage and player.state.cash + money_from_mortgages < self.turn_amount_owed:
                found_a_prop_to_mortgage = False
                prop_to_mortgage = self.decision_utils.best_property_to_mortgage(game_state, player, sim_property_set_for_mortgage_calcs)
                if not prop_to_mortgage is None:
                    list_of_properties_to_mortgage.append(prop_to_mortgage.original_property)
                    money_from_mortgages = money_from_mortgages + int(prop_to_mortgage.price / 2)
                    found_a_prop_to_mortgage = True
                    sim_property_set_for_mortgage_calcs.remove(prop_to_mortgage)
            if player.state.cash + money_from_mortgages < self.turn_amount_owed:
                self.panic_selling = 0
        if not(list_of_properties_to_mortgage is None) or len(list_of_properties_to_mortgage)>0:
            self.number_mortgaged_properties=self.number_mortgaged_properties + len (list_of_properties_to_mortgage)
        return list_of_properties_to_mortgage

    def max_cash_obtained_by_mortgaging_properties(self, game_state, my_own_player, sim_property_list):
        #This function returns the amount of cash that would be obtained by mortgaging properties
        #We need this because mortgaging properties is better than selling houses
        properties_to_mortgage=[]
        #Calculate income for mortgaging all properties (where no houses are in any set)
        #Return the amount raised
        cash_from_mortgaging = 0
        for prop in sim_property_list:
            if self.board_utils.is_station(prop.name) or self.board_utils.is_utility(prop.name):
                cash_from_mortgaging = cash_from_mortgaging + int(prop.price / 2)
            elif prop in self.board_utils.get_list_of_complete_sets_i_own(game_state.board, my_own_player):
                #We own all the properties - make sure none of them have houses on
                max_houses=[p.sim_number_of_houses for p in prop.property_set.properties]
                if max_houses == 0:
                    cash_from_mortgaging = cash_from_mortgaging + int(prop.price / 2)

        return cash_from_mortgaging

    def ai_error(self, message):
        '''
        Called if the return value from any of the Player AI functions
        was invalid. for example, if it was not of the expected type.

        No response is required.
        '''
        pass

    def property_offered_for_auction(self, game_state, player, property):
        property_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state, property, player)
        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)

        money_needed_in_future=self.cash_buffer_required(game_state,player)\
                               - house_building_instructions_and_cost.get(2)
        #If anyone (including myself) would get a monopoly, then offer up to 1.5 times the value
        multiplier=1
        for check_player in game_state.players:
            total_monopolies_player_would_own=self.decision_utils.number_of_monopolies_player_would_get(
                                             [property],check_player)
            if total_monopolies_player_would_own > 1:
                multiplier=3
                break
        if(player.state.cash - money_needed_in_future )> 0:
            return min(player.state.cash - money_needed_in_future, multiplier * property_worth)
        return 0

    def deal_proposed(self, game_state, player, deal_proposal):
        real_prop=None
        total_offered=0
        total_monopolies_i_would_own=0
        total_monopolies_proposer_would_own = 0
        player_proposing=deal_proposal.proposed_by_player
        for prop in deal_proposal.properties_offered:
            total_offered = total_offered + self.decision_utils.amount_property_is_worth_to_a_player(game_state,prop,
                                        player)
            #Check if it would give me a monopoly
            total_monopolies_i_would_own=total_monopolies_i_would_own + \
                                         self.decision_utils.number_of_monopolies_player_would_get(
                                             deal_proposal.properties_offered,player)

        total_wanted=0
        for prop in deal_proposal.properties_wanted:
            if player.is_same_player(prop.property_set.owner):
                #Trying to buy a property that is part of a Monopoly I own - REJECT
                return DealResponse(DealResponse.Action.REJECT)

            total_wanted = total_wanted + self.decision_utils.amount_property_is_worth_to_a_player(game_state,prop,
                                        player)
            #print ('Opponent wants: ' + str(prop.name))
            if player_proposing is not None:
                total_monopolies_proposer_would_own=total_monopolies_proposer_would_own + \
                                         self.decision_utils.number_of_monopolies_player_would_get(
                                             deal_proposal.properties_offered,player_proposing)
        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)
        money_needed_in_future=self.cash_buffer_required(game_state,player)\
                               - house_building_instructions_and_cost.get(2)
        #We know who this player is
        if total_monopolies_i_would_own >=total_monopolies_proposer_would_own:
            if total_offered >= total_wanted:
                return DealResponse(DealResponse.Action.ACCEPT,
                                        maximum_cash_offered=max(0,
                                                                 min(player.state.cash-money_needed_in_future*3,
                                                                     0.3*total_offered-total_wanted)))
            return DealResponse(DealResponse.Action.REJECT)

    def propose_deal(self, game_state, player):
        self.turndealcount = self.turndealcount + 1
        if self.turndealcount == 3:
            self.turndealcount = 0
            return None
        if self.turndealcount==2:
            return None
        #Has anyone got properties that would give us a monopoly?
        #Has anyone got properties where we own some and others are still available?
        #Has anyone got properties with a "high" expected return?
        #How likely are people to accept deals? Can we record this info and use it in future to make offers
        #that are more likely to be accepted?

        #Has this player ALREADY rejected a deal in this turn from us?
        #i.e. - Can we offer something more appealing?
            #Attempt 1 - Just cash
            #Attempt 2 - Properties + cash that WOULDN'T give them a monopoly
            #Attempt 3 - Properties + cash that WOULD give them a monopoly

        all_my_properties=self.board_utils.get_properties_i_own(game_state.board,player)
        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)

        for my_prop in all_my_properties:
            num_set_i_own = 1
            num_set_owned_by_no_one = 0
            prop_in_set_owned_by_only_one_other = False
            owners_of_this_set=[]
            sole_other_owner = None
            props_in_set_to_ask_for=[]
            if not my_prop.owner == my_prop.property_set.owner:
                #We have a property but don't own the set
                for other_prop in my_prop.property_set.properties:
                    if other_prop.name != my_prop.name:
                        if not other_prop.owner is None:
                            if player.is_same_player(other_prop.owner):
                                num_set_i_own=num_set_i_own+1
                            else:
                                if not(owners_of_this_set.__contains__(other_prop.owner)):
                                    owners_of_this_set.append(other_prop.owner)
                                    sole_other_owner = other_prop.owner
                                    props_in_set_to_ask_for.append(other_prop)
                        else:
                            num_set_owned_by_no_one=num_set_owned_by_no_one+1
            if len(my_prop.property_set.properties) == 2:
                #Offer for the other property if owned by someone
                if len(owners_of_this_set) == 1:
                    amount_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state, 
                       props_in_set_to_ask_for[0] , player)
                    spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player) 
                        - house_building_instructions_and_cost.get(2))
                    amount_to_offer=max(0,min(spare_cash,amount_worth/2))

                    return DealProposal(
                        propose_to_player= sole_other_owner,
                        properties_offered=None,
                        properties_wanted=props_in_set_to_ask_for,
                        maximum_cash_offered=amount_to_offer)

            if len(my_prop.property_set.properties) == 3:
                #Offer for the other property if owned by someone
                if len(owners_of_this_set) == 1:
                    amount_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state, 
                        props_in_set_to_ask_for[0], player)
                    spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player) 
                        - house_building_instructions_and_cost.get(2))
                    if len( props_in_set_to_ask_for) == 2:
                        amount_worth_2 = amount_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state, 
                            props_in_set_to_ask_for[1] , player)
                        amount_worth = amount_worth + amount_worth_2
                    amount_to_offer=max(0,min(spare_cash,amount_worth/2))

                    return DealProposal(
                        propose_to_player= sole_other_owner,
                        properties_offered=None,
                        properties_wanted=props_in_set_to_ask_for,
                        maximum_cash_offered=amount_to_offer)

        #props_where_i_dont_own_monopoly_but_others_own_some.append(my_prop)

        #It's more important to get ONE monopoly - so don't package up things where I could get SEVERAL monopolies
        #People won't accept that
        #TODO: Unless they are dumb
        #What about the BEST monopoly to get? How to work that out?
        #What if this player NEVER accepts a deal? Are we wasting our "deal-making" ability?
        i_can_get_a_monopoly=False

        total_value_of_what_i_want = 0

        return None