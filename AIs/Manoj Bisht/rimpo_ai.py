from monopyly import *
from operator import itemgetter, attrgetter
from monopyly.utility import *
from math import *

class Mycalculate:

    pass

class RimpoAI(PlayerAIBase):
    '''
    An AI that plays like Sophie.

    She only buys the stations and Mayfair and Park Lane, and
    will enter into fairly generous deals to get hold of them.
    '''
    NO_OF_HOUSES = 0
    TOTAL_PROPS = 1
    MY_PROPS = 2
    UNOWNED_PROPS = 3

    def __init__(self):
        '''
        The 'constructor'.
        '''

        #will contain property of color set remaining to own from my property.

        #self.preferred_color_list = []

        #self.cash_reserve = 0
        #self.cash_reserve_when_building_houses = 0


        self.cash_deduction = 0
        self.player = None
        self.game_state = None

        self.cash_needed = 0
        self.prop_group_map = None

    def get_name(self):
        '''
        Returns this AI's name.
        '''
        return "RimpoAI"



    def start_of_game(self):
        self.cash_reserve = 250
        self.cash_reserve_when_building_houses = 100
        self.cash_reserve_when_unmortgage = 100
        self.cash_reserve_for_staying_in_jail = 300
        self.cash_reserve_high_risky_pocket_stretch = 0 #very risky business. properties might get mortgaged
        self.cash_reserve_medium_risky_pocket_stretch = 75 #medium risky business
        self.cash_reserve_low_risky_pocket_stretch = 150 # risky



        self.me = None
        self.game_state = None
        self.cash_needed = 0
        self.prop_group_map = {}
        #                                        [no_of_houses,total_no_of_props,props_i_own,props_unowned]
        self.prop_group_map[PropertySet.BROWN] = [0,2,0,2]
        self.prop_group_map[PropertySet.LIGHT_BLUE] = [0,3,0,3]
        self.prop_group_map[PropertySet.PURPLE] = [0,3,0,3]
        self.prop_group_map[PropertySet.ORANGE] = [0,3,0,3]
        self.prop_group_map[PropertySet.RED] = [0,3,0,3]
        self.prop_group_map[PropertySet.YELLOW] = [0,3,0,3]
        self.prop_group_map[PropertySet.GREEN] = [0,3,0,3]
        self.prop_group_map[PropertySet.DARK_BLUE] = [0,2,0,2]
        self.prop_group_map[PropertySet.STATION] = [0,4,0,4]
        self.prop_group_map[PropertySet.UTILITY] = [0,2,0,2]
        self.favorite_set = [PropertySet.ORANGE,
                             PropertySet.STATION,
                             PropertySet.DARK_BLUE,
                             PropertySet.RED,
                             PropertySet.YELLOW,
                             PropertySet.GREEN]

        self.total_no_of_houses = 0
        self.big_bid = False
        pass

    def start_of_turn(self, game_state, player):

        if self.game_state is None:
            self.game_state = game_state

        if self.me is None:
            if player.name == self.get_name():
                self.me = player
        pass

    def net_worth(self):
        '''
        Returns the player's net worth, which includes their
        cash, properties and houses.
        '''
        # Net worth includes cash...
        total = self.me.state.cash

        for p in self.me.state.properties:
            # We add the mortgage value of properties...
            if p.is_mortgaged is False:
                total += p.mortgage_value

                # We add the resale value of houses...
                if type(property) == Street:
                    total += int(p.house_price/2 * p.number_of_houses)

        return total

    def net_asset(self):
        '''
        Returns the player's net worth, which includes their
        cash, properties and houses.
        '''
        # Net worth includes cash...
        total = 0

        for p in self.me.state.properties:
            # We add the mortgage value of properties...
            if p.is_mortgaged is False:
                total += p.mortgage_value

                # We add the resale value of houses...
                if type(property) == Street:
                    total += int(p.house_price/2 * p.number_of_houses)

        return total

    def net_asset_basic(self, excluded_set):

         total = self.me.state.cash

         for p in self.me.state.properties:
            # We add the mortgage value of properties...
            if p.is_mortgaged is False:
                if p.property_set != excluded_set:
                    if p.property_set not in self.me.state.owned_unmortgaged_sets:
                        total += p.mortgage_value
                # We add the resale value of houses...
                #if type(property) == Street:
                #total += int(p.house_price/2 * p.number_of_houses)

         return total

    #----------------------------------buy properties--------------------------------------
    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when we land on an unowned property.
        '''
        # We want to buy the property, but do we have enough money?
        if player.state.cash > self.cash_reserve + property.price:
            self.prop_group_map[property.property_set.set_enum][RimpoAI.MY_PROPS] += 1
            return PlayerAIBase.Action.BUY

        #desirability based pocket stretch
        val = self.prop_group_map[property.property_set.set_enum]

        if (val[RimpoAI.MY_PROPS]+1)/val[RimpoAI.TOTAL_PROPS] > 0.5:

            if val[RimpoAI.TOTAL_PROPS] - val[RimpoAI.MY_PROPS] == 1:
                if property.property_set.set_enum in self.favorite_set:
                    return PlayerAIBase.Action.BUY
                else:
                    if self.net_asset_basic(property.property_set) > self.cash_reserve_medium_risky_pocket_stretch + property.price:
                        return PlayerAIBase.Action.BUY

        if property.property_set.set_enum in self.favorite_set:
            if player.state.cash > self.cash_reserve_low_risky_pocket_stretch + property.price:
                return PlayerAIBase.Action.BUY

        return PlayerAIBase.Action.DO_NOT_BUY

        pass
    #-------------------------auction properties case----------------------------------

    def property_offered_for_auction(self, game_state, player, property):

        val = self.prop_group_map[property.property_set.set_enum]

        ret = property.price
        #desirability is high if i own more properties
        if (val[RimpoAI.MY_PROPS]+1)/val[RimpoAI.TOTAL_PROPS] > 0.5:
            #need to stretch pocket to the limit and take risk.
            if val[RimpoAI.TOTAL_PROPS]- val[RimpoAI.MY_PROPS] == 1:

                if property.property_set.set_enum in self.favorite_set:
                    ret = self.net_asset_basic(property.property_set) - self.cash_reserve_medium_risky_pocket_stretch
                else:
                    #not a fav set
                    ret = self.net_asset_basic(property.property_set) - self.cash_reserve_low_risky_pocket_stretch

            else:
                #normal stretch
                ret = player.state.cash - self.cash_reserve_low_risky_pocket_stretch
        else:
            if player.state.cash > self.cash_reserve + property.price:
                ret = property.price + property.price*0.1
            else:
                if player.state.cash > property.price + 50:
                    ret = property.price + 1



        if ret > 1000:
            self.big_bid = True
        #not enough cash cases.

        #less bid case
        if ret < property.price:
            for p in game_state.players:
                if p != self.me and p.state.cash > property.price:
                    ret = property.price

        if ret < 0:
            ret = property.price

        #print ("my bid: %d cash:%d for name:%s set:%s price:%d" %(ret,self.me.state.cash,property.name,property.property_set.set_enum,property.price))
        return ret


    def auction_result(self, status, property, player, amount_paid):
        if status == PlayerAIBase.Action.AUCTION_SUCCEEDED:
            if player == self.me:
                self.prop_group_map[property.property_set.set_enum][RimpoAI.MY_PROPS] += 1
            #else:
            #print("won paid:%d by player:%s cash:%d for name:%s set:%s price:%d" %(amount_paid,player.name,player.state.cash,property.name,property.property_set.set_enum,property.price))
        pass

    #-----------------------deal making-----------------------------------------------------------
    def propose_deal(self, game_state, player):

        props_wanted_ = []
        ##   if arr[RimpoAI.TOTAL_PROPS] - arr[RimpoAI.MY_PROPS] == 1:
          #      for p in player.state.properties:
                    #props_wanted.append()

        return None

    def deal_proposed(self, game_state, player, deal_proposal):

        return DealResponse(DealResponse.Action.REJECT)

    def deal_result(self, deal_info):

        pass

    def deal_completed(self, deal_result):

        pass

    #----------------------sell scenarios----------------------------------------------------------

    def money_will_be_taken(self, player, amount):
        self.cash_deduction = amount
        self.cash_needed = amount - player.state.cash

        #in case of cash_needed is 0 we dont need to sell anything.
        #negative implies we have enough cash
        if self.cash_needed < 0:
           self.cash_needed = 0

        pass

    def build_houses(self, game_state, player):
        '''
        always tries to build houses if i have money.
        '''
        ret = []
        total_cost = 0

        #print ("---new buy----")
        #print (self.prop_group_map)
        for owned_set in player.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                    continue
            #fetching total number of houses in this property set for getting the starting point
            no_of_houses = self.prop_group_map[owned_set.set_enum][0]
            idx = no_of_houses % owned_set.number_of_properties

            #append houses to list till money is enough
            while total_cost + owned_set.properties[idx].house_price + self.cash_reserve_when_building_houses < player.state.cash and no_of_houses < owned_set.number_of_properties*5:
                ret.append((owned_set.properties[idx],1))
                #print("%s %d %d" % (owned_set.properties[idx].name,1,no_of_houses))
                total_cost += owned_set.properties[idx].house_price
                no_of_houses += 1
                idx = (idx+1) % owned_set.number_of_properties
            #updating total number of houses in this property set
            self.prop_group_map[owned_set.set_enum][0] = no_of_houses

            #if no_of_houses > 0:
            #    print ("buy %s %d %d" % (owned_set.set_enum,no_of_houses,self.prop_group_map[owned_set.set_enum][0]))

        #print ("check %d" % (self.prop_group_map[owned_set.set_enum][0]))
        self.total_no_of_houses += len(ret)
        return ret

    def _check_mortgaging_properties_is_enough(self):
        total_cash = 0
        for p in self.me.state.properties:
            if p.property_set not in self.me.state.owned_unmortgaged_sets:
                if total_cash < self.cash_needed:
                    total_cash += p.price/2
                else:
                    break

        if total_cash > self.cash_needed:
            return True

        return False
    def sell_houses(self, game_state, player):

        ret = []

        #nothing to be done. enough money
        if self.cash_needed == 0:
            return ret

        #Bankruptcy!! :(
        if self.net_worth() < self.cash_needed:
            #print ("bankruptcy sell_houses %d %d" % (player.net_worth,self.cash_needed))
            return ret

        #let mortgage_props do the selling keep the houses
        if self.total_no_of_houses > 0:
            if self._check_mortgaging_properties_is_enough():
                return ret

        cash_generated = 0

        for owned_set in player.state.owned_unmortgaged_sets:
             if not owned_set.can_build_houses:
                    continue

             #fetching total number of houses in this property set for getting the starting point
             no_of_houses = self.prop_group_map[owned_set.set_enum][0]
             idx = (no_of_houses - 1) % owned_set.number_of_properties

             #if no_of_houses > 0:
             #    print ("sell %s %d" % (owned_set.set_enum,no_of_houses))

             #append houses to list house needs to be sold
             while cash_generated < self.cash_needed and no_of_houses > 0:
                 ret.append((owned_set.properties[idx],1))

                 cash_generated += owned_set.properties[idx].house_price/2

                 no_of_houses -= 1

                 #stupid logic for decremental circular idx
                 idx -= 1
                 if idx < 0:
                        idx = owned_set.number_of_properties - 1

             self.prop_group_map[owned_set.set_enum][0] =  no_of_houses

             #print ("sell %s %d %d %d" % (owned_set.set_enum,self.prop_group_map[owned_set.set_enum][0],cash_generated,self.cash_needed))




        if self.cash_needed < cash_generated:
            #no need of further properties mortgaging.
            self.cash_needed = 0
        else:
            #no option left. need to mortgage properties :`(
            self.cash_needed -= cash_generated
            #print ("houses sold %d %d" % (self.cash_needed,cash_generated))

        self.total_no_of_houses -= len(ret)
        return ret
    #-------------------------------- mortgage/unmortgage properties--------------
    def mortgage_properties(self, game_state, player):

        ret = []

        #nothing to be done. enough money
        if self.cash_needed == 0:
            return ret

        #Bankruptcy!! :(
        if self.net_worth() < self.cash_needed:
            #print ("bankruptcy morg %d %d" % (player.net_worth, self.cash_needed))
            return ret

        lst = []
        rent = 0
        for p in player.state.properties:

            if p.is_mortgaged:
                continue

            if isinstance(p,Street):
                if p.number_of_houses == 0:
                    rent = p.rents[0]
                    owner = p.owner
                    if p.property_set in player.state.owned_unmortgaged_sets:
                        # The player owns the whole set, so the rent is doubled...
                        rent *= 2
                else:
                    # The street has houses, so we find the rent for the number
                    # of houses there are...
                    rent = p.rents[p.number_of_houses]

            elif isinstance(p,Station):
                board = game_state.board
                owned_stations = board.get_property_set(PropertySet.STATION).intersection(player.state.properties)
                number_of_owned_stations = len(owned_stations)

                if number_of_owned_stations == 1:
                    rent = 25
                elif number_of_owned_stations == 2:
                    rent = 50
                elif number_of_owned_stations == 3:
                    rent = 100
                elif number_of_owned_stations == 4:
                    rent = 200

            elif isinstance(p,Utility):
                board = game_state.board
                owned_utilities = board.get_property_set(PropertySet.UTILITY).intersection(player.state.properties)
                number_of_owned_utilities = len(owned_utilities)

                if number_of_owned_utilities == 1:
                    rent = 28
                elif number_of_owned_utilities == 2:
                    rent = 70

            lst.append((p,rent))

        #sorted(lst, key=itemgetter(1))
        cash_generated = 0
        for p,rent in sorted(lst, key=itemgetter(1)):
            if p.is_mortgaged is False:
                if cash_generated < self.cash_needed:
                    ret.append(p)
                    cash_generated += p.price/2

                    # mortgaged props are considered not my props (to reduce desireability)
                    self.prop_group_map[p.property_set.set_enum][RimpoAI.MY_PROPS] -= 1
                else:
                    #done
                    break

        #print ("morgated %d %d" % (cash_generated,self.cash_needed))
        #if len(ret) > 0:
        #    print (ret)
        self.cash_needed = 0
        return ret


    def unmortgage_properties(self, game_state, player):
        ret = []
        total_cost = 0
        no_of_owned_set = len(player.state.owned_unmortgaged_sets)
        #properties which will complete set will be given priority
        for p in player.state.properties:
            if p.is_mortgaged:
                arr = self.prop_group_map[p.property_set.set_enum]

                #desirable property. this will compelete me a set
                if arr[RimpoAI.TOTAL_PROPS] - arr[RimpoAI.MY_PROPS] == 1:
                    cost = p.price/2 + p.price*0.1

                    #take risk to complete this set.
                    if p.property_set.set_enum in self.favorite_set:
                        if total_cost + cost + self.cash_reserve_high_risky_pocket_stretch < player.state.cash:
                            ret.append(p)
                            total_cost += cost
                            self.prop_group_map[p.property_set.set_enum][RimpoAI.MY_PROPS] += 1
                            no_of_owned_set += 1
                    else:
                        if total_cost + cost + self.cash_reserve_medium_risky_pocket_stretch < player.state.cash:
                            ret.append(p)
                            total_cost += cost
                            self.prop_group_map[p.property_set.set_enum][RimpoAI.MY_PROPS] += 1
                            no_of_owned_set += 1


        #already have set, prefer making houses.
        for owned_set in player.state.owned_unmortgaged_sets:
                if owned_set.can_build_houses:
                    #if len(ret) > 0:
                    #    print ("unmortgage {0}".format(ret))
                    return ret

        for p in player.state.properties:
            if p.is_mortgaged:

                val = p.price/2 + p.price*0.1
                if total_cost + val + self.cash_reserve_low_risky_pocket_stretch < player.state.cash:
                    ret.append(p)
                    total_cost += val

                    # unmortgaged props are considered my props again(to reduce desireability)
                    self.prop_group_map[p.property_set.set_enum][RimpoAI.MY_PROPS] += 1
                else:
                    break

        #if len(ret) > 0:
        #   print ("unmortgage {0}".format(ret))
        return ret
    #------------------------------- all jail conditions-----------------------------------
    def players_birthday(self):
        return "Happy Birthday!"

    def get_out_of_jail(self, game_state, player):

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
        if player.state.cash <= self.cash_reserve_for_staying_in_jail:
            PlayerAIBase.Action.STAY_IN_JAIL

        #If you are here. Now try to be out of jail.
        if player.state.number_of_get_out_of_jail_free_cards > 0:
            PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD

        #buy your way out
        return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL

    def player_went_bankrupt(self, player):
         #if player.name == self.get_name():
         #   Logger.log("I am bhikari. {0} {1} {2} {3} {4}".format(len(player.state.properties),len(player.state.owned_unmortgaged_sets),self.total_no_of_houses,self.net_worth(),self.net_asset()),Logger.WARNING)
         pass

    def player_ran_out_of_time(self, player):

         #if player.name == self.get_name():
         #    print ("Come on. dont remove me")
         pass
    def game_over(self, winner, maximum_rounds_played):

        #if self.big_bid and winner != self.me:
        #    print ("problem")
        #if winner.name == self.get_name():
        #     print ("Wooo Hooo!! I won")
        #print (maximum_rounds_played)
        #Logger.log("over. my {0} {1} {2} {3} {4}".format(len(self.me.state.properties),len(self.me.state.owned_unmortgaged_sets),self.total_no_of_houses,self.net_worth(),self.net_asset()),Logger.WARNING)
        pass