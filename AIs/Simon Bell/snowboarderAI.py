###########################################################
## File        : SnowboarderAI.py
## Description : 

from monopyly import *
from monopyly.utility import Logger

from .snowboarderDB import SnowboarderDB

# Class Dependencies

class SnowboarderAI(PlayerAIBase):

# Class Attributes


# Constructor

    def __init__(self):

# Instance Attributes

        self.db=SnowboarderDB()
        self.targetSquareGroup=['Red','Yellow','Green','Dark blue']
        self.positionFactor=0.8
        self.cashReserveLower=100
        self.cashReserveUpper=500
        self.cashReserve=self.cashReserveLower
        self.cashReserveIncrement=20
        self.bidFactor=2
        self.propertyCountLower=6
        self.proposedDealCount=0
        self.proposedDealList=[]
        self.moneyNeeded=0

# Class Initialisation
        return

# Operations

    def get_name(self):
        return 'Snowboarder'

    def start_of_game(self):
        return super(SnowboarderAI,self).start_of_game()

    def start_of_turn(self,game_state,player):
        if player.name==self.get_name(): # Is it me?
            max_net_worth=0
            otherPlayers=[otherPlayer for otherPlayer in game_state.players if otherPlayer.name!=self.get_name()]
            for otherPlayer in otherPlayers:
                if otherPlayer.net_worth>max_net_worth:
                    max_net_worth=otherPlayer.net_worth
            Logger.log("Position={0}".format(player.net_worth-max_net_worth,))
            if player.net_worth>round(max_net_worth*self.positionFactor): # Am I in contention?
                if self.cashReserve<self.cashReserveUpper:
                    self.cashReserve+=self.cashReserveIncrement # Save for a rainy day!
            else:
                if self.cashReserve>self.cashReserveLower:
                    self.cashReserve-=self.cashReserveIncrement # Go for it!
            Logger.log("Reserve={0}".format(self.cashReserve,))
            ownedPropertyNames=[property.name for property in player.state.properties]
            Logger.log("Properties owned="+str(ownedPropertyNames))
            self.db.UpdateOwnership(ownedPropertyNames)
            self.proposedDealList=self.db.FindMissingProperties()
            self.proposedDealCount=0
            Logger.log("Properties wanted="+str(self.proposedDealList))
        return super(SnowboarderAI,self).start_of_turn(game_state,player)

    def player_landed_on_square(self,game_state,square,player):
        return super(SnowboarderAI,self).player_landed_on_square(game_state,square,player)

    def landed_on_unowned_property(self,game_state,player,property):
        if self.want_property(game_state,player,property):
            if player.state.cash>(self.cashReserve+property.price):
                Logger.log(self.get_name()+" buying: "+property.name)
                return PlayerAIBase.Action.BUY
            else:
                Logger.log(self.get_name()+" can't buy: {0}, price: {1}, cash: {2}, reserve: {3}".format(property.name,property.price,player.state.cash,self.cashReserve,))
        return PlayerAIBase.Action.DO_NOT_BUY

    def money_will_be_taken(self,player,amount):
        if amount>player.state.cash:
            self.moneyNeeded=amount-player.state.cash # Need to mortgage stuff or sell it
        else:
            self.moneyNeeded=0
        return super(SnowboarderAI,self).money_will_be_taken(player,amount)

    def money_taken(self,player,amount):
        return super(SnowboarderAI,self).money_taken(player,amount)

    def money_given(self,player,amount):
        return super(SnowboarderAI,self).money_given(player,amount)

    def got_get_out_of_jail_free_card(self):
        return super(SnowboarderAI,self).got_get_out_of_jail_free_card()

    def players_birthday(self):
        return super(SnowboarderAI,self).players_birthday()

    def pay_ten_pounds_or_take_a_chance(self,game_state,player):
        return super(SnowboarderAI,self).pay_ten_pounds_or_take_a_chance(game_state,player)

    def property_offered_for_auction(self,game_state,player,property):
        if self.want_property(game_state,player,property):
            bid=round(property.price*self.bidFactor) # Too simplistic
            if player.state.cash>(self.cashReserve+bid):
                Logger.log(self.get_name()+" bidding: "+property.name)
                return bid
            else:
                if player.state.cash>self.cashReserve:
                    Logger.log(self.get_name()+" bidding: "+property.name)
                    return player.state.cash-self.cashReserve # Bid what we can afford
                else:
                    Logger.log(self.get_name()+" can't bid: {0}, price: {1}, cash: {2}, reserve: {3}".format(property.name,property.price,player.state.cash,self.cashReserve,))
        return 0

    def build_houses(self,game_state,player):
        for owned_set in player.state.owned_unmortgaged_sets:
            if not owned_set.can_build_houses:
                continue
            cost=owned_set.house_price*owned_set.number_of_properties
            if player.state.cash>(self.cashReserveLower+cost):
                return [(p, 1) for p in owned_set.properties] # We build one house on each property...
        return []

    def sell_houses(self,game_state,player):
        if self.moneyNeeded>0:
            cash_raised=0
            properties_to_sell=[]
            #for property in player.state.properties:
            #    if cash_raised>self.moneyNeeded:
            #        break
            #    if not property.is_mortgaged:
            #        if str(property.property_set)=='Station' or str(property.property_set)=='Utility':
            #            properties_to_sell.append(property)
            #            cash_raised+=round(property.price*0.5)
            for owned_set in player.state.owned_unmortgaged_sets:
                if cash_raised>self.moneyNeeded:
                    break
                for property in player.board._property_set_map[owned_set.set_enum].properties:
                    if isinstance(property, Street) and (property.number_of_houses > 0):
                        properties_to_sell.append((property,1))
            return properties_to_sell
        return []

    def mortgage_properties(self,game_state,player):
        properties_to_mortgage=[]
        for property in player.state.properties:
            if not property.is_mortgaged:
                if str(property.property_set)!='Station' and str(property.property_set)!='Utility':
                    if property.number_of_houses==0:
                        if not property.property_set.__str__() in player.state.owned_unmortgaged_sets:
                            properties_to_mortgage.append(property)
                else:
                    properties_to_mortgage.append(property)
        return properties_to_mortgage

    def unmortgage_properties(self,game_state,player):
        starting_cash=player.state.cash
        unmortgage=[]
        for owned_set in player.state.owned_sets:
            for property in player.board._property_set_map[owned_set.set_enum].properties:
                if property.is_mortgaged:
                    if starting_cash>property.mortgage_value: # Forget reserve when unmortgaging
                        unmortgage.append(property)
                        starting_cash-=property.mortgage_value
        return unmortgage

    def get_out_of_jail(self, game_state, player):
        return super(SnowboarderAI,self).get_out_of_jail(game_state, player)

    def propose_deal(self,game_state,player):
        deal_proposal = DealProposal()
        if len(self.proposedDealList)>self.proposedDealCount:
            propertyName=self.proposedDealList[self.proposedDealCount][0]
            self.proposedDealCount+=1
            property=game_state.board.squares[player.board._name_to_index_map[propertyName][0]]
            bid=property.price*self.bidFactor # Too simplistic
            if player.state.cash>(self.cashReserve+bid):
                return DealProposal(
                    properties_wanted=[property],
                    maximum_cash_offered=bid,
                    propose_to_player=property.owner)
            else:
                if player.state.cash>self.cashReserve:
                    return DealProposal(
                        properties_wanted=[property],
                        maximum_cash_offered=player.state.cash-self.cashReserve, # Bid what we can afford
                        propose_to_player=property.owner)
        return super(SnowboarderAI,self).propose_deal(game_state,player)

    def deal_proposed(self,game_state,player,deal_proposal):
        if len(deal_proposal.properties_offered) > 0:
            return DealResponse(DealResponse.Action.REJECT)
        if len(deal_proposal.properties_wanted) > 1:
            return DealResponse(DealResponse.Action.REJECT)
        property = deal_proposal.properties_wanted[0]
        squareGroup=property.property_set.__str__()
        if squareGroup!=None:
            if squareGroup in self.targetSquareGroup:
                return DealResponse(DealResponse.Action.REJECT)
            else:
                return DealResponse(
                    action=DealResponse.Action.ACCEPT,
                    minimum_cash_wanted=round(property.price*1.5)) # We'll accept as long as the price offered is greater than the original selling price...

    def deal_result(self,deal_info):
        return super(SnowboarderAI,self).deal_result(deal_info)

    def player_went_bankrupt(self,player):
        return super(SnowboarderAI,self).player_went_bankrupt(player)

    def want_property(self,game_state,player,property):
        try:
            if len(player.state.properties)<self.propertyCountLower: # Get a 'critical mass' of properties for trading
                if player.board._name_to_index_map[property.name][0]>player.board._name_to_index_map["Jail"][0]:
                    return True
                else:
                    return False
            else:
                if str(property.property_set)!='Station' and str(property.property_set)!='Utility':
                    squareGroup=property.property_set.__str__()
                    if squareGroup!=None:
                        if squareGroup in self.targetSquareGroup:
                            return True
        except Exception as err:
            Logger.log("Exception thrown in 'landed_on_unowned_property': "+str(err))
        return False

    def property_value(self,game_state,player,property):
        return

    def ai_error(self,message):
        return super(SnowboarderAI,self).ai_error(message)

