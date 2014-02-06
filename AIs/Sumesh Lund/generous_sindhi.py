from monopyly import *
import operator
import copy

        
class GenerousSindhiAI(PlayerAIBase):
    '''
    An AI that concentrates on keeping assets and building houses wisely.
    '''
    class return_on_investment():
        '''Used to make collection of the street names sorted w.r.t ROI '''
        def __init__(self, street_name, is_mortgaged, number_of_houses, house_price, price, property_set, ROI):
            self.street_name = street_name
            self.is_mortgaged = is_mortgaged
            self.house_price = house_price
            self.number_of_houses = number_of_houses
            self.ROI = ROI
            self.property_set = property_set
            self.price = price
        
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cash_reserve = 100
        self.cash_reserve_when_auctioning = 100
        self.cash_reserve_when_unmortgage = 200
        self.roi_list = None
        self.cash_needed = 0
        self.actual_net_worth_var = 0

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Generous Sindhi"

    def actual_net_worth(self, player):
        total = player.state.cash

        for property in player.state.properties:
            # We add the mortgage value of properties...
            if not property.is_mortgaged:
                total += property.mortgage_value

                # We add the resale value of houses...
                if type(property) == Street:
                    total += int(property.house_price/2 * property.number_of_houses)
        return total

    def money_will_be_taken(self, player, amount):
        '''
        Calculates the cash_needed
        '''
        self.money_deduction = amount
        #self.cash_needed = amount - player.state.cash
        self.cash_needed = amount

        #in case of cash_needed is 0 we dont need to sell anything.
        #negative implies we have enough cash
        if self.cash_needed < 0:
            self.cash_needed = 0
           
        pass

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        '''
        Called when the player picks up the "Pay a ??10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
        return PlayerAIBase.Action.PAY_TEN_POUND_FINE

    def sell_houses(self, game_state, player):
        '''
        Sindhi chooses what to sell wisely
        '''
        ret = []

        #Check cash needed.
        if (player.state.cash-self.cash_needed) >= 0:
            return ret

        #No money Left. Let's get high!
        if self.actual_net_worth(player) < self.cash_needed:
            return ret

        self._calculate_return_on_investment(game_state, player, False)
        cash_generated = 0
        temp_mort = 0

        while((self.cash_needed - player.state.cash) > (cash_generated + temp_mort)):
            for p in self.roi_list:
                if((self.cash_needed - player.state.cash) > (cash_generated + temp_mort)):
                    if (p.number_of_houses > 0):
                        if p.number_of_houses == self._get_max_houses(p.property_set):
                            street_obj = self._get_street_obj(player,p.street_name)
                            ret.append((street_obj, 1))
                            cash_generated += p.house_price / 2
                            p.number_of_houses -= 1
                    else:
                        if not p.is_mortgaged:
                            temp_mort += p.price/2
                            p.is_mortgaged = True
                else:
                    break

        if (cash_generated + player.state.cash < self.cash_needed):
            pass
        else:
            self.cash_needed = 0

        return ret

    def _get_street_obj(self, player, street_name):
        for x in player.state.properties:
            if x.name == street_name:
                return x


    def _get_max_houses(self, property_set):
        '''Return the maximum number of houses built on a particular property in a set '''
        max = 0

        for prop in self.roi_list:
            if prop.property_set == property_set:
                if prop.number_of_houses > max:
                    max = prop.number_of_houses
        return max

    def get_out_of_jail(self, game_state, player):
        '''
        Called in the player's turn, before the dice are rolled, if the player
        is in jail.
        '''

        sold = 0

        for p in game_state.players:
            sold += len(p.state.properties)


        #checking if most of the properties are sold. prefer staying into jail
        #total number of properties in monoply is 28
        if sold / 28 > 0.65:
            #most of the properties are not mine.
            if len(player.state.properties)/sold < 0.75:
                return PlayerAIBase.Action.STAY_IN_JAIL

        #cash reserve is very low. prefer staying into jail
        if player.state.cash <= 100:
            PlayerAIBase.Action.STAY_IN_JAIL

        #If you are here. Now try to be out of jail.
        if player.state.number_of_get_out_of_jail_free_cards > 0:
            PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD

        #buy your way out
        return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL

    def propose_deal(self, game_state, player):
        '''
        Called to allow the player to propose a deal.
        '''
        return None

    def mortgage_properties(self, game_state, player):
        '''
        Sindhi chooses what to mortgage wisely
        '''
        ret = []

        self.actual_net_worth_var = self.actual_net_worth(player)

        #Check cash needed.
        if (player.state.cash-self.cash_needed) >= 0:
            return ret

        #Give me money! I am Bankrupt!
        if self.actual_net_worth(player) < self.cash_needed:
            return ret
        
        self._calculate_return_on_investment(game_state, player, False)
        cash_generated = 0
        for p in self.roi_list:
            if cash_generated < (self.cash_needed - player.state.cash) and not p.is_mortgaged:
                cash_generated += p.price/2
                street_obj = self._get_street_obj(player, p.street_name)
                ret.append(street_obj)
                p.is_mortgaged = True
            else:
                break
                
        self.cash_needed = 0
        return ret

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Buys as much as possible to increase the spread on the board.
        '''
        if player.state.cash > (self.cash_reserve + property.price):
            return PlayerAIBase.Action.BUY
        else:
            return PlayerAIBase.Action.DO_NOT_BUY

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''
        # We only accept deals for single properties wanted from us...
        if len(deal_proposal.properties_offered) > 0:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)

        # We'll accept as long as the price offered is greater than
        # the original selling price...
        property = deal_proposal.properties_wanted[0]
        return DealResponse(
            action=DealResponse.Action.ACCEPT,
            minimum_cash_wanted=property.price+200)

    def build_houses(self, game_state, player):
        '''
        Bob the Builder. So many IFs.. I know!
        '''
        # We calculate the return on investment for each property owned...
        self._calculate_return_on_investment(game_state, player, True)
        ret = []
        #iterate the roi list from top to bottom
        cash_to_be_used = copy.deepcopy(player.state.cash)
        for p in self.roi_list:
            if (p.property_set != PropertySet.STATION and p.property_set != PropertySet.UTILITY):
            #iterate owned sets
                for owned_set in player.state.owned_unmortgaged_sets:
                    #check if we own the set for the element in ROI
                    if(owned_set.set_enum == p.property_set):
                        #check if we have the money to buy atleast one house
                        if cash_to_be_used > (self.cash_reserve + owned_set.house_price):
                            #check if we can build a house
                            if(p.number_of_houses <= self._get_min_houses(owned_set) and owned_set.can_build_houses):
                                for x in owned_set.properties:
                                    if x.name == p.street_name:
                                        ret.append((x, 1))
                                        p.number_of_houses += 1
                                        cash_to_be_used -= owned_set.house_price
                                break

        return ret

    def _get_min_houses(self, property_set):
        '''Return the minimum number of houses built on a particular property in a set '''
        minimum = 0

        for prop in self.roi_list:
            if prop.property_set == property_set:
                if prop.number_of_houses < minimum:
                    minimum = prop.number_of_houses
        return minimum

    def _calculate_return_on_investment(self, game_state, player, rev_flag):
        '''Computes the ROI for building houses on each owned property. 
        This helps deciding where to build the house first. '''
        rent = 0
        
        self.roi_list = []
        for p in player.state.properties:
            
            house_price = 0
            price = 0
            is_mortgaged = False
            number_of_houses = 0
            property_set = None
            if p.is_mortgaged:
                continue
            if isinstance(p, Street):
                rent = self.calculate_rent_street(p, player)
                house_price = p.house_price
                price = p.price
                is_mortgaged = copy.deepcopy(p.is_mortgaged)
                number_of_houses = copy.deepcopy(p.number_of_houses)
                property_set = p.property_set.set_enum
            elif isinstance(p, Station):
                rent = self.calculate_rent_station(game_state, p)
                price = p.price
                is_mortgaged = copy.deepcopy(p.is_mortgaged)
                property_set = p.property_set.set_enum
                p.price
            elif isinstance(p, Utility):
                rent = self.calculate_rent_utility(game_state, p)
                price = p.price
                is_mortgaged = copy.deepcopy(p.is_mortgaged)
                property_set = p.property_set.set_enum

            self.roi_list.append(self.return_on_investment(p.name, is_mortgaged, number_of_houses,
                                 house_price, price, property_set, (rent - house_price/2)))

        self.roi_list.sort(key = operator.attrgetter('ROI'), reverse = rev_flag)

    def calculate_rent_street(self, property, player):
        '''
        The player has landed on a square owned by another player
        and must pay rent.
        '''
        # Are there any houses?
        if property.number_of_houses == 0:
            rent = property.rents[0]
            if property.property_set in player.state.owned_unmortgaged_sets:
                # The player owns the whole set, so the rent is doubled...
                rent *= 2
        else:
            # The street has houses, so we find the rent for the number
            # of houses there are...
            rent = property.rents[property.number_of_houses]

        return rent
        
    def calculate_rent_station(self, game_state, property):
        '''
        The rent depends on how many station the owner owns.
        '''
        # We find how many stations the owner has...
        board = game_state.board
        owned_stations = board.get_property_set(PropertySet.STATION).intersection(property.owner.state.properties)
        number_of_owned_stations = len(owned_stations)

        if number_of_owned_stations == 1:
            return 25
        elif number_of_owned_stations == 2:
            return 50
        elif number_of_owned_stations == 3:
            return 100
        elif number_of_owned_stations == 4:
            return 200

        return 0

    def calculate_rent_utility(self, game_state, property):
        '''
        The rent is 4x the roll of the dice if the owner has
        one utility, 10x if they have both.
        '''
        # We find how many utilities the owner has...
        board = game_state.board
        owned_utilities = board.get_property_set(PropertySet.UTILITY).intersection(property.owner.state.properties)
        number_of_owned_utilities = len(owned_utilities)

        if number_of_owned_utilities == 1:
            return 4 * 3
        elif number_of_owned_utilities == 2:
            return 10 * 3

        return 0

    def property_offered_for_auction(self, game_state, player, property):
        '''
        If only one property is left to complete a set, we auction higher.
        '''

        (dict_desire, dict_number) = self._list_important_properties(player)
        auction_price = property.price + property.price*dict_desire[str(property.property_set)]

        no_of_properties_remaining =(property.property_set.number_of_properties - dict_number[property.property_set.set_enum])

        if no_of_properties_remaining == 1:

            if(player.state.cash > auction_price):
                return auction_price
            else:
                cash_needed_to_buy = auction_price

                if (self.actual_net_worth(player)+self.cash_reserve_when_auctioning) < cash_needed_to_buy:
                    #Cannot Buy
                    return 0
                else:
                    return auction_price
        else:
            if(player.state.cash > (self.cash_reserve_when_auctioning + auction_price)):
                return auction_price
            else:
                return 0
    
    def _list_important_properties(self, player):
        '''Return a dict of properties with percentage for desirability'''
        dict_desire = {PropertySet.BROWN:0.0, PropertySet.LIGHT_BLUE:0.0, PropertySet.PURPLE:0.0, PropertySet.ORANGE:0.0, PropertySet.RED:0.0,
                PropertySet.YELLOW:0.0, PropertySet.GREEN:0.0, PropertySet.DARK_BLUE:0.0, PropertySet.STATION:0.0, PropertySet.UTILITY:0.0}

        dict_number = {PropertySet.BROWN:0.0, PropertySet.LIGHT_BLUE:0.0, PropertySet.PURPLE:0.0, PropertySet.ORANGE:0.0, PropertySet.RED:0.0,
                PropertySet.YELLOW:0.0, PropertySet.GREEN:0.0, PropertySet.DARK_BLUE:0.0, PropertySet.STATION:0.0, PropertySet.UTILITY:0.0}
        
        for p in player.state.properties:

            dict_number[p.property_set.set_enum] += 1
            dict_desire[str(p.property_set)] = dict_number[p.property_set.set_enum]/p.property_set.number_of_properties
            
        return (dict_desire, dict_number)
    
    def unmortgage_properties(self, game_state, player):
        '''
        Sindhi unmortgages if he has cash.
        '''

        ret = []
        total_cost = 0

        for p in player.state.properties:
            if p.is_mortgaged:
                val = p.price/2 + p.price*0.1
                if total_cost + val + 1 + self.cash_reserve_when_unmortgage < player.state.cash:
                    ret.append(p)
                    total_cost += val + 1
                else:
                    break
        return ret

    def players_birthday(self):
        '''
        Sindhi doesn't want to lose money :P.
        '''
        return "Happy Birthday!"
    
    def player_went_bankrupt(self, player):

        #if player.name == self.get_name():
            #print("BANKRUPT!!!!!")
        pass

    def player_ran_out_of_time(self, player):

        #if player.name == self.get_name():
        #    print ("Ran out of time. Seriously!? :/")
        pass

    def game_over(self, winner, maximum_rounds_played):

        #if winner.name == self.get_name():
            #print ("Jai Jhulelal!")
        pass