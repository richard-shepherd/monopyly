from monopyly import *
import operator
import traceback
import copy

        
class MumbaikarAI(PlayerAIBase):
    '''
    An AI that concentrates on keeping assets and building houses wisely.
    '''
    class return_on_investment():
        '''Used to make collection of the street names sorted w.r.t ROI '''
        def __init__(self, street_name, ROI):
            self.street_name = street_name
            self.ROI = ROI
        
    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cash_reserve = 500
        self.cash_reserve_when_auctioning = 300
        self.cash_reserve_when_unmortgage = 300
        self.roi_list = None
        self.cash_needed = 0
        self.actual_net_worth_var = 0

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Mumbaikar"

    def actual_net_worth(self, player):
        total = player.state.cash

        for property in player.state.properties:
            # We add the mortgage value of properties...
            if not property.is_mortgaged:
                total += property.mortgage_value

                # We add the resale value of houses...
                if type(property) == Street:
                    total += int(property.house_price/2 * property.number_of_houses)
        #total -=  player.state.cash
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
        Mumbaikar chooses what to sell wisely
        '''
        ret = []
        #print('inside sell_houses')
        #self.actual_net_worth_var = self.actual_net_worth(player)


        #print("inside sell. net worth:%d, cash: %d, cash needed:%d" % (self.actual_net_worth(player),player.state.cash,self.cash_needed))
        #Check cash needed.
        if self.cash_needed == 0:
            return ret
        if player.state.cash > self.cash_needed:
            return ret

        #Bankruptcy!! :(
        if self.actual_net_worth(player) < self.cash_needed:
            #print ("bankruptcy sell %d %d" % (self.actual_net_worth(player),self.cash_needed))
            return ret

        self._calculate_return_on_investment(game_state, player, False)
        cash_generated = 0
        temp_mort = 0
        itr_count = 0
        mort_prop = []

        while((self.cash_needed - player.state.cash) > (cash_generated + temp_mort)):
            for p in self.roi_list:
                if( (self.cash_needed - player.state.cash) > (cash_generated + temp_mort) ):
                    if isinstance(p.street_name, Street) and (p.street_name.number_of_houses - itr_count > 0):
                        if p.street_name.number_of_houses == self._get_max_houses(p.street_name.property_set):
                            ret.append((p.street_name, 1))
                            cash_generated += p.street_name.property_set.house_price / 2
                    else:
                        if not mort_prop.__contains__(p.street_name.name):
                            temp_mort += p.street_name.mortgage_value
                            mort_prop.append(p.street_name.name)
                else:
                    break
            itr_count += 1
            if itr_count > 100:
                break

        #for prop in player.state.properties:
        #    if isinstance(prop, Street):
        #        print(str(prop.number_of_houses), str(prop))
        #        if(prop.number_of_houses < 0):
        #            print('wait')
        #    else:
        #        print(str(prop))

        if (cash_generated + player.state.cash < self.cash_needed):
            self.cash_needed -= cash_generated
        else:
            self.cash_needed = 0
        return ret

    def _get_max_houses(self, property_set):
        '''Return the maximum number of houses built on a particular property in a set '''
        max = 0

        for ow in property_set.properties:
            if ow.number_of_houses > max:
                max = ow.number_of_houses
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
        Mumbaikar chooses what to mortgage wisely
        '''
        ret = []
        #print('inside mortgage_properties')

        self.actual_net_worth_var = self.actual_net_worth(player)

        #print("Inside Mortgage. Net worth:%d, Cash: %d, Cash Needed:%d" % (self.actual_net_worth(player),player.state.cash,self.cash_needed))
        #Check cash needed.
        if self.cash_needed == 0:
            return ret

        #Bankruptcy!! :(
        if self.actual_net_worth(player) < self.cash_needed:
            #print ("bankruptcy mortgage %d %d" % (self.actual_net_worth(player),self.cash_needed))
            return ret
        
        self._calculate_return_on_investment(game_state, player, False)
        cash_generated = 0
        for p in self.roi_list:
            if cash_generated < (self.cash_needed - player.state.cash):
                cash_generated += p.street_name.mortgage_value
                ret.append(p.street_name)
            else:
                break
                
        if(cash_generated + player.state.cash < self.cash_needed):
           self.cash_needed -= cash_generated
        else:
            self.cash_needed = 0
        return ret

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property. We always buy it if we
        can while keeping a small cash reserve.
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
            minimum_cash_wanted=property.price+1)

    def build_houses(self, game_state, player):
        '''
        Building houses as per ROI
        '''
        #print('inside build_houses')
        # We calculate the return on investment for each property owned...
        self._calculate_return_on_investment(game_state, player, True)
        ret = []
        #iterate the roi list from top to bottom
        for p in self.roi_list:
            if isinstance(p.street_name, Street):
            #iterate owned sets
                for owned_set in player.state.owned_unmortgaged_sets:
                    #check if we own the set for the element in ROI
                    if(owned_set == p.street_name.property_set):
                        #check if we have the money to buy atleast one house
                        if player.state.cash > (self.cash_reserve + owned_set.house_price):
                            #check if we can build a house
                            if(p.street_name.number_of_houses <= self._get_min_houses(owned_set)):
                                if(owned_set.can_build_houses):
                                    ret.append((p.street_name,1))
                                    break

        return ret
    
    def _get_min_houses(self, owned_set):
        '''Return the minimum number of houses built on a particular property in a set '''
        mini = 0
        index = 0
        for ow in owned_set.properties:
            if index == 0 or (ow.number_of_houses < mini):
                mini = ow.number_of_houses
                index  += 1
        return mini

    def _calculate_return_on_investment(self, game_state, player, rev_flag):
        '''Computes the ROI for building houses on each owned property. 
        This helps deciding where to build the house first. '''
        rent = 0
        
        self.roi_list = []
        for p in player.state.properties:
            
            house_price = 0
            if p.is_mortgaged:
                continue
            if isinstance(p,Street):
                rent = self.calculate_rent_street(p, player)
                house_price = p.house_price
            elif isinstance(p,Station):
                rent = self.calculate_rent_station(game_state, p)
            elif isinstance(p,Utility):
                rent = self.calculate_rent_utility(game_state, p)
            
            self.roi_list.append(self.return_on_investment(p,(rent - house_price/2)))

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
        We offer the face  plus or minus a random amount.
        '''
        #This will be useful to predict if in future I should auction this property. 
        #Coz I can get more money during auction.

        #print('inside property_offered_for_auction')
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
        '''Return a dict of properties with percentage '''
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
        Mumbaikar unmortgages if he has cash.
        '''
        #print('inside unmortgage_properties')

        ret = []
        total_cost = 0
        self._calculate_return_on_investment(game_state, player, True)

        for roi in self.roi_list:
            for p in player.state.properties:
                if roi.street_name == p:
                    if p.is_mortgaged:
                        val = p.price/2 + p.price*0.1
                        if total_cost + val + self.cash_reserve_when_unmortgage < player.state.cash:
                            ret.append(p)
                            total_cost += val
                        else:
                            break

        #if len(ret) > 0:
        #   print (ret)
        return ret

    def players_birthday(self):
        '''
        Mumbaikar doesn't want to lose money :P.
        '''
        return "Happy Birthday!"
    
    def player_went_bankrupt(self, player):

        #if player.name == self.get_name():
        #    print("No Money!")
        pass

    def player_ran_out_of_time(self, player):

        #if player.name == self.get_name():
        #    print ("Not over yet!")
        pass

    def game_over(self, winner, maximum_rounds_played):

        #if winner.name == self.get_name():
        #    print ("I am a Money Magnet!")
        pass
            
