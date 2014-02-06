from monopyly import *
from random import *
from .jamestyasbasics import *

class PimpMyBoard(JamesTyasBasicsAI):
    '''
    This AI counts its number of turns in a game

    '''
    def __init__(self):
        self.total_games = 0
        self.total_turns = 0
        self.panic_selling = 0
        self.turn_amount_owed = 0
        self.property_probs=PropertyProbCalcs()
        self.board_utils=BoardUtils(self.property_probs)
        self.decision_utils=DecisionUtils(self.property_probs)
        self.turndealcount=0
        self.players_who_will_swap_from_completed_sets = []
        self.players_who_wont_swap_from_completed_sets = []
        self.proposing_deal_cash_only=False
        self.proposing_deal_including_props=False
        self.proposing_deal_including_prop_and_cash=False
        self.proposing_trick_deal=False
        self.proposing_to_player=None


    def get_name(self):
        return "PimpMyBoard"

    def property_offered_for_auction(self, game_state, player, property):
        # Dont offer for stations or utilities
        if (self.board_utils.is_station(property.name)
                or self.board_utils.is_utility(property.name)):
            return 0

        property_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state, property, player)

        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)

        money_needed_in_future=self.cash_buffer_required(game_state,player)\
                               - house_building_instructions_and_cost.get(2)
        #If anyone would get a monopoly, then offer up to 3 times the value
        multiplier=1
        for check_player in game_state.players:
            #Multiply by three if I would own monopoly
            total_monopolies_player_would_own=self.decision_utils.number_of_monopolies_player_would_get(
                                             [property],check_player)
            if total_monopolies_player_would_own > 1:
                if check_player.is_same_player(player):
                    multiplier=3
                    break
                else:
                    #Multiply by two  if someone else would own monopoly
                    multiplier=2
                    break
        multiplier=1
        #Ignore multiplier
        if(player.state.cash - money_needed_in_future )> 0:
            return max(0,min(player.state.cash - money_needed_in_future, multiplier * property_worth))
        return 0

    def cash_buffer_required(self, game_state, my_own_player):
        if not self.cash_buffer_required_saved==-999:
            return self.cash_buffer_required_saved

        max_loss_single_roll = self.board_utils.max_loss_single_roll(game_state, my_own_player)

        self.cash_buffer_required_saved=max_loss_single_roll
        return self.cash_buffer_required_saved

    def unmortgage_properties(self, game_state, player):
        # Order of events is: make deals, unmortgage properties, build houses
        # Do we prefer to build houses or unmortgage?
        if self.number_mortgaged_properties == 0:
            #No properties to unmortgage
            return []
        cost_for_house_improvements=self.house_building_instructions_and_cost(game_state, player).get(2)
        available_cash_for_unmortgaging=player.state.cash - self.cash_buffer_required(game_state,player) \
                                        - cost_for_house_improvements
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
            set_not_owned = False
            prop_to_unmortgage = self.decision_utils.best_property_to_unmortgage(game_state, player,
                                                                                 sim_property_set_for_mortgage_calcs)
            if not prop_to_unmortgage is None:
                #Don't bother unmortgaging if we don't own the set
                list_of_properties_to_unmortgage.append(prop_to_unmortgage.original_property)
                cost_to_unmortgage = cost_to_unmortgage + int(prop_to_unmortgage.price * 0.55)
                if not(prop_to_unmortgage.original_property.owner
                           == prop_to_unmortgage.original_property.property_set.owner):
                    set_not_owned = True

                if set_not_owned or (cost_to_unmortgage > available_cash_for_unmortgaging):
                    #The best property to unmortgage cost TOO much
                    #Continue calculating BUT don't include it in the final decision
                     list_of_properties_to_unmortgage.remove(prop_to_unmortgage.original_property)
                     cost_to_unmortgage = cost_to_unmortgage - int(prop_to_unmortgage.price * 0.55)

                found_a_prop_to_mortgage = True
                sim_property_set_for_mortgage_calcs.remove(prop_to_unmortgage)
        if len(list_of_properties_to_unmortgage) >0:
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
        else:
            #Not panic selling BUT what about mortgage all properties if we have a set AND the other properties
            # aren't available
            my_sets = self.board_utils.get_list_of_complete_sets_i_own(game_state.board, player)
            if len(my_sets)>1:
                #I own at least one set - let's mortgage properties where others own each of the other properties in
                # the rest of the set
                props_i_own=self.board_utils.get_properties_i_own(game_state.board, player)
                for prop_to_mortgage in props_i_own:
                    #A property in the set is free
                    prop_is_free = False
                    if not(prop_to_mortgage.owner==prop_to_mortgage.property_set.owner):
                        #I don't own this set
                        for prop_in_set in prop_to_mortgage.property_set.properties:
                            if prop_in_set.owner is None:
                                prop_is_free = True
                                break
                        if prop_is_free == False:
                            #No free properties in set, mortgage this one
                             list_of_properties_to_mortgage.append(prop_to_mortgage)

        if list_of_properties_to_mortgage is None or len(list_of_properties_to_mortgage)>0:
            self.number_mortgaged_properties=self.number_mortgaged_properties + len (list_of_properties_to_mortgage)
        return list_of_properties_to_mortgage


    def propose_deal(self, game_state, player):

        self.deal_turn_count=self.deal_turn_count + 1
        #Has anyone got properties that would give us a monopoly?
        #Has anyone got properties where we own some and others are still available?
        #Has anyone got properties with a "high" expected return?
        #How likely are people to accept deals? Can we record this info and use it in future to make offers
        #that are more likely to be accepted?

        #self.players_who_will_swap_from_completed_sets = []
        #self.players_who_wont_swap_from_completed_sets = []


        all_my_properties=self.board_utils.get_properties_i_own(game_state.board,player)
        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)

        # Look for sets where I can get a monopoly by buying from a player (so no offers if a square still free
        # in that set)
        found_a_property_to_ask_for = False
        for my_prop in all_my_properties:
            # Can I get a monopoly by buying one prop from ONE other player (and no free squares)
            # Ignore stations and utilities
            if self.board_utils.is_station(my_prop.name) or self.board_utils.is_utility(my_prop.name):
                continue
            recommended_proposal=self.can_get_monopoly_from_one_player(game_state, player,my_prop)
            #Expects to receive [Property to ask for,player to offer to]
            if not(recommended_proposal is None) and len(recommended_proposal)>0:
                amount_worth=self.decision_utils.amount_property_is_worth_to_a_player(game_state,
                        recommended_proposal[0] , player)
                #Get property AND owner name
                # Is there a double  rejection count for this property?
                if recommended_proposal[0] in self.properties_with_double_rejection :
                    #Try finding a deal for the next property
                    #Is this our third deal attempt in a turn
                    if not(recommended_proposal[0] in self.properties_with_triple_rejection):
                        #TODO:Finish third time proposal and deal logging includimg LARGE CASH
                   
                        prop_to_offer = self.find_prop_to_offer_another_player(game_state, player,
                        recommended_proposal[1] )
                        if not( prop_to_offer) is None:
                            #3rd attempt so cash plus property
                            spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player)
                                - house_building_instructions_and_cost.get(2))
                            self.proposing_deal_including_prop_and_cash = True
                            self.proposing_deal_property=recommended_proposal[0]
                            self.proposing_to_player=recommended_proposal[1]
                            amount_to_offer=max(0,min(spare_cash,amount_worth))

                            return DealProposal(
                                propose_to_player= recommended_proposal[1],
                                properties_offered= [prop_to_offer],
                                properties_wanted=[recommended_proposal[0]],
                                maximum_cash_offered=amount_to_offer)

                    else:
                        #TODO:Third attempt but they didnt accept cash
                        # and we dont have a property that gives them a monopoly
                        #Could offer random stations and utilities and cash
                        continue

                # Have we tried cash for this prop before in this game?
                if recommended_proposal[0] in self.properties_tried_cash_only:
                    #TODO: Offer to swap for where they get a monopoly
                    # Or triple cash
                    prop_to_offer = self.find_prop_to_offer_another_player(game_state, player,
                        recommended_proposal[1] )
                    if not( prop_to_offer) is None:
                        
                        spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player)
                            - house_building_instructions_and_cost.get(2))
                  
                        self.proposing_deal_including_props = True
                        self.proposing_deal_property=recommended_proposal[0]
                        self.proposing_to_player=recommended_proposal[1]
                        return DealProposal(
                            propose_to_player= recommended_proposal[1],
                            properties_offered= [prop_to_offer],
                            properties_wanted=[recommended_proposal[0]],
                            maximum_cash_offered=0)

                    else:
                        #Second attempt but no good prop to offer them
                        #Try a different property
                        continue
                        # spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player)
                        #     - house_building_instructions_and_cost.get(2))
                        # self.proposing_deal_including_props = True
                        # self.proposing_deal_property=recommended_proposal[0]
                        # self.proposing_to_player=recommended_proposal[1]
                        # amount_to_offer=max(0,min(spare_cash,amount_worth))
                        
                        return DealProposal(
                            propose_to_player= recommended_proposal[1],
                            properties_offered= [],
                            properties_wanted=[recommended_proposal[0]],
                            maximum_cash_offered=amount_to_offer)
                #TODO: Offer cash only
                #Multiply amount by 3 - it is a monopoly after all
                spare_cash = ( player.state.cash-self.cash_buffer_required(game_state,player)
                        - house_building_instructions_and_cost.get(2))
                amount_to_offer=max(0,min(spare_cash,amount_worth))

                self.proposing_deal_cash_only = True
                self.proposing_deal_property=recommended_proposal[0]
                self.proposing_to_player=recommended_proposal[1]
                return DealProposal(
                        propose_to_player= recommended_proposal[1],
                        properties_offered=None,
                        properties_wanted=[recommended_proposal[0]],
                        maximum_cash_offered=amount_to_offer)
            else:
                #This property can't get us a monopoly try the next
                continue
        #If we get here then we can try a trick deal - because there aren't any useful properties to us


        # Once found try a cash deal
        # If rejected, then log this rejection for this player against this property with the amount offered

        # Second time, try offering cash plus a property where they get a monopoly
        # if this is not possible, triple the cash offered

        # Third time - trick deal - try and get someone to give me their monopoly (without houses)
        # offer 2 times cash
        # log result to self.players_who_will_swap_from_completed_sets = []
        # or self.players_who_wont_swap_from_completed_sets = []

        # After this - DON'T try and offer for the same property in this game UNLESS there's nothing else
        # we want to try - in which case go again (i.e. count number of triple rejections on a prop in a game)



        pass

    def can_get_monopoly_from_one_player(self,game_state, player,my_prop):
        #Expects to return
        #[Property to ask for,player to offer to]
        num_set_player_owns = 1
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
                            num_set_player_owns=num_set_player_owns+1
                        else:

                            #Check it's not because we're looking to offer a property to a player
                            if not(other_prop.owner in owners_of_this_set):
                                owners_of_this_set.append(other_prop.owner)
                                props_in_set_to_ask_for.append(other_prop)
                            if len(owners_of_this_set) >1:
                                break
                    else:
                        num_set_owned_by_no_one=num_set_owned_by_no_one+1
                        break

#       if num_set_owned_by_no_one >=1:
            #Properties in this set still available
#            return None
        if len(owners_of_this_set) == 1:
            #This will be 1 if there is only one other property and only one owner
            return [props_in_set_to_ask_for[0],owners_of_this_set[0]]

        return None

    def find_prop_to_offer_another_player(self, game_state, my_player,
                other_player):

        all_my_properties=self.board_utils.get_properties_i_own(game_state.board,my_player)
        for prop_to_offer in all_my_properties:
            # Don't offer properties where i could get monop
            check_for_monop_poss= self.can_get_monopoly_from_one_player(game_state, my_player,prop_to_offer)
            if check_for_monop_poss is None or len(check_for_monop_poss)==0:
                # We cant get a monop with this prop,can the other person?
                check_for_monop_for_other=self.can_get_monopoly_from_one_player(game_state, other_player,prop_to_offer)
                if (not( check_for_monop_for_other is None) and
                    len( check_for_monop_for_other)>0):
                    return check_for_monop_for_other[0]
        return

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property.
        '''
        #Buy all the stations
        #If this will get us a monopoly OR prevent someone else getting a monopoly - then buy it
        max_sets_owned_by_others=0
        for check_player in game_state.players:
            if len(check_player.state.owned_sets)>max_sets_owned_by_others:
                max_sets_owned_by_others=len(check_player.state.owned_sets)
            if self.decision_utils.number_of_monopolies_player_would_get([property],player) >=1:
                #It gives a monopoly - take a risk and buy it
                if player.state.cash > property.price:
                    return PlayerAIBase.Action.BUY
                else:
                    return PlayerAIBase.Action.DO_NOT_BUY
        #If I own 4 monopolies and own equal or greater than the best other player
        #allow for house improvements in my calcs
        cost_for_house_improvements=self.house_building_instructions_and_cost(game_state, player).get(2)
        if not(player.state.owned_sets is None):
            if len(player.state.owned_sets)>=4 and len(player.state.owned_sets)>=max_sets_owned_by_others:

                if (player.state.cash - self.cash_buffer_required(game_state,player)-cost_for_house_improvements>
                        property.price):
                    return PlayerAIBase.Action.BUY
                else:
                    return PlayerAIBase.Action.DO_NOT_BUY

        #To get here either we own less than four sets
        #OR someone else owns more sets than us
        #AND this property won't give us a monopoly

        #Are we saving for any good sets?

        max_i_need=0
        check_my_saving_for_set_purchase=self.max_property_cost_if_i_can_get_set(game_state,player,PropertySet.ORANGE)
        if check_my_saving_for_set_purchase>0 and property.property_set.set_enum== PropertySet.ORANGE:
        #This is the property we want!
            if (player.state.cash - self.cash_buffer_required(game_state,player)>
                property.price):
                return PlayerAIBase.Action.BUY
            else:
                return PlayerAIBase.Action.DO_NOT_BUY
        if max_i_need<check_my_saving_for_set_purchase:
            max_i_need=check_my_saving_for_set_purchase

        check_my_saving_for_set_purchase=self.max_property_cost_if_i_can_get_set(game_state,player,PropertySet.RED)
        if check_my_saving_for_set_purchase>0 and property.property_set.set_enum== PropertySet.RED:
        #This is the property we want!
            if (player.state.cash - self.cash_buffer_required(game_state,player)>
                property.price):
                return PlayerAIBase.Action.BUY
            else:
                return PlayerAIBase.Action.DO_NOT_BUY
        if max_i_need<check_my_saving_for_set_purchase:
            max_i_need=check_my_saving_for_set_purchase

        check_my_saving_for_set_purchase=self.max_property_cost_if_i_can_get_set(game_state,player,PropertySet.LIGHT_BLUE)
        if check_my_saving_for_set_purchase>0 and property.property_set.set_enum== PropertySet.LIGHT_BLUE:
            #This is the property we want!
            if (player.state.cash - self.cash_buffer_required(game_state,player)>
                property.price):
                return PlayerAIBase.Action.BUY
            else:
                return PlayerAIBase.Action.DO_NOT_BUY

        if max_i_need<check_my_saving_for_set_purchase:
            max_i_need=check_my_saving_for_set_purchase

        check_my_saving_for_set_purchase=self.max_property_cost_if_i_can_get_set(game_state,player,PropertySet.YELLOW)
        if check_my_saving_for_set_purchase>0 and property.property_set.set_enum== PropertySet.YELLOW:
            #This is the property we want!
            if (player.state.cash - self.cash_buffer_required(game_state,player)>
                property.price):
                return PlayerAIBase.Action.BUY
            else:
                return PlayerAIBase.Action.DO_NOT_BUY

        if max_i_need<check_my_saving_for_set_purchase:
            max_i_need=check_my_saving_for_set_purchase
            #Buy it if we're not saving for anything else in particular
        if (player.state.cash - self.cash_buffer_required(game_state,player)-cost_for_house_improvements-max_i_need>
                property.price):
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY


    def max_property_cost_if_i_can_get_set(self,game_state,player,property_set):
        #This function returns the cost of the most expensive unpurchased property in a set
        #that no-one else owns, or only i own
        all_props_in_set=game_state.board.get_properties_for_set(property_set)
        max_unpurchased_cost=0
        for check_prop in all_props_in_set:
            if not(check_prop.owner is None) and not(player.is_same_player(check_prop.owner)):
                #Someone else owns something in this set
                return 0
            if check_prop.owner is None:
                if max_unpurchased_cost<check_prop.price:
                    max_unpurchased_cost=check_prop.price
        return max_unpurchased_cost

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
                total_monopolies_proposer_would_own=total_monopolies_proposer_would_own+\
                                                    self.decision_utils.number_of_monopolies_player_would_get(
                                             deal_proposal.properties_offered,player_proposing)
        house_building_instructions_and_cost=self.house_building_instructions_and_cost(game_state,player)
        money_needed_in_future=self.cash_buffer_required(game_state,player)\
                               - house_building_instructions_and_cost.get(2)
        #We know who this player is
        if total_monopolies_i_would_own >total_monopolies_proposer_would_own:
                return DealResponse(DealResponse.Action.ACCEPT,
                                        maximum_cash_offered=max(0,
                                                                 min(player.state.cash-money_needed_in_future,
                                                                     max(0,total_offered-total_wanted))))
        if total_monopolies_i_would_own==total_monopolies_proposer_would_own and total_monopolies_i_would_own>0:
            if total_offered >= total_wanted:
                return DealResponse(DealResponse.Action.ACCEPT,
                                        maximum_cash_offered=max(0,
                                                                 min(player.state.cash-money_needed_in_future,
                                                                     total_offered-total_wanted)))
            #They are offering a cash only deal or they get more monopolies than we would, reject
        return DealResponse(DealResponse.Action.REJECT)

    def deal_result(self, deal_info):
        #TODO: All the logging as a result of a deal

        #self.properties_with_double_rejection=[]
        #self.properties_tried_cash_only=[]

        # Check that it is ME proposing a deal and not receiving one
        if not(self.proposing_deal_cash_only == True
            or self.proposing_deal_including_props == True
            or self.proposing_trick_deal == True
            or self.proposing_deal_including_prop_and_cash == True):
            return

        if (deal_info == PlayerAIBase.DealInfo.DEAL_REJECTED
            or deal_info == PlayerAIBase.DealInfo.ASKED_FOR_TOO_MUCH_MONEY
            or deal_info == PlayerAIBase.DealInfo.OFFERED_TOO_LITTLE_MONEY
            or deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY):

            if self.proposing_deal_cash_only == True:
                self.properties_tried_cash_only.append(self.proposing_deal_property)
            if self.proposing_deal_including_props == True:
                self.properties_with_double_rejection.append(self.proposing_deal_property)
            if self.proposing_deal_including_prop_and_cash==True:
                self.properties_with_triple_rejection.append(self.proposing_deal_property)
        if self.proposing_trick_deal== True:
            if (deal_info ==PlayerAIBase.DealInfo.SUCCEEDED):
                self.players_who_will_swap_from_completed_sets.append(self.proposing_to_player)
            else:
                self.players_who_wont_swap_from_completed_sets.append(self.proposing_to_player)
        self.proposing_deal_cash_only=False
        self.proposing_deal_including_props=False
        self.proposing_trick_deal=False
        self.proposing_to_player=None
        self.proposing_deal_property=None
        self.proposing_deal_including_prop_and_cash=False


