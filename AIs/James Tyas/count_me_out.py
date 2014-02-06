from monopyly import *
from random import *
from .jamestyasbasics import *

class CountMeOut(JamesTyasBasicsAI):
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

    def get_name(self):
        return "CountMeOut"
    
    def propose_deal(self, game_state, player):
        return None

    def propose_deal(self, game_state, player):
        self.turndealcount = self.turndealcount + 1
        #Only one deal per turn
        if self.turndealcount > 1:
            return None

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
                    amount_to_offer=min(spare_cash,amount_worth/2)
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
                    amount_to_offer=min(spare_cash,amount_worth/2)

                    return DealProposal(
                        propose_to_player= sole_other_owner,
                        properties_offered=None,
                        properties_wanted=props_in_set_to_ask_for,
                        maximum_cash_offered=amount_to_offer)

        return None