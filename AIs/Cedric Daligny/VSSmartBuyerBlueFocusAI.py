__author__ = 'Cedric'
# each information will be used to sort the properties for the given policy
import random

from monopyly import *
from .Memory import *
from .Policy import *


class VSSmartBuyerBlueFocusAI(PlayerAIBase):
    '''
    '''
    def __init__(self):
        '''
        ctor
        '''
        # memory information
        self.needed_money = 0

        self.auction_memory = AuctionMemory()
        self.deal_memory = DealMemory()
        self.property_policy = AcquiringPolicy(self)
        self.house_policy = HousePolicy_v2(self,HousePolicy_v2.HousePolicy.ONE_COMPLETE_SET, HousePolicy_v2.RepartitionPolicy.SAME_SIZE)
        self.selling_policy = SellingPolicy(self,self.deal_memory)

        self.chance_policy = ChancePolicy(0.2)
        self.jail_policy = JailPolicy(0.8, 3, 20)
        self.money_to_be_taken = 0
        self.properties_information = {
            #brown
            Square.Name.OLD_KENT_ROAD:          [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.WHITECHAPEL_ROAD:       [300, 1, 1, 1, 250, 4, 0.75],
            #light blue
            Square.Name.THE_ANGEL_ISLINGTON:    [0, 1.25, 1.25, 1.25, 50, 9, 0.75],
            Square.Name.EUSTON_ROAD:            [0, 1.25, 1.25, 1.25, 50, 9, 0.75],
            Square.Name.PENTONVILLE_ROAD:       [0, 1.25, 1.25, 1.25, 0, 10, 0.75],
            #rose
            Square.Name.PALL_MALL:              [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.WHITEHALL:              [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.NORTHUMBERLAND_AVENUE:  [300, 1, 1, 1, 250, 5, 0.75],
            #orange
            Square.Name.BOW_STREET:             [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.MARLBOROUGH_STREET:     [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.VINE_STREET:            [300, 1, 1, 1, 250, 5, 0.75],
            #red
            Square.Name.STRAND:                 [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.FLEET_STREET:           [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.TRAFALGAR_SQUARE:       [300, 1, 1, 1, 250, 5, 0.75],
            #yellow
            Square.Name.LEICESTER_SQUARE:       [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.COVENTRY_STREET:        [300, 1, 1, 1, 250, 4, 0.75],
            Square.Name.PICCADILLY:             [300, 1, 1, 1, 250, 5, 0.75],
            #green
            Square.Name.REGENT_STREET:          [300, 1, 1, 1, 250, 5, 0.75],
            Square.Name.OXFORD_STREET:          [300, 1, 1, 1, 250, 5, 0.75],
            Square.Name.BOND_STREET:            [300, 1, 1, 1, 250, 5, 0.75],
            #dark blue
            Square.Name.PARK_LANE:              [0, 1.25, 1.25, 1.25, 50, 9, 0.75],
            Square.Name.MAYFAIR:                [0, 1.25, 1.25, 1.25, 0, 10, 0.75],
            #station
            Square.Name.KINGS_CROSS_STATION:        [150, 1.15, 1.15, 1.25, 0, -1, 0],
            Square.Name.MARYLEBONE_STATION:         [150, 1.15, 1.15, 1.25, 0, -1, 0],
            Square.Name.FENCHURCH_STREET_STATION:   [150, 1.15, 1.15, 1.25, 0, -1, 0],
            Square.Name.LIVERPOOL_STREET_STATION:   [150, 1.15, 1.15, 1.25, 0, -1, 0],
            #company
            Square.Name.ELECTRIC_COMPANY:           [250, 1.15, 1.15, 1, 0, -1, 0.5],
            Square.Name.WATER_WORKS:                [250, 1.15, 1.15, 1, 0, -1, 0.5],
        }

    def get_name(self):
        return 'VSSmartBuyerBlueFocusAI'

    def start_of_game(self):
        '''
        Called at the start of the game.

        No response is required.
        '''
        self.needed_money = 0
        self.money_to_be_taken = 0

    def start_of_turn(self, game_state, player):
        '''
        Called when an AI's turn starts. All AIs receive this notification.

        No response is required.
        '''
        self.needed_money = 0
        self.money_to_be_taken = 0

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        return self.property_policy.acquire_through_landing(game_state,player,property)

    def money_given(self, player, amount):
        '''
        Called when money has been given to the player.

        No response is required.
        '''
        pass

    def money_will_be_taken(self, player, amount):
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.
        '''
        self.money_to_be_taken = amount
        if amount > player.state.cash:
            self.needed_money = amount - player.state.cash
        pass

    def money_taken(self, player, amount):
        '''
        Called when money has been taken from the player.

        No response is required.
        '''
        pass

    def players_birthday(self):
        '''
        Called when a player picks up the 'It is your birthday...'
        Community Chest card.

        You should return "Happy Birthday!" (with this casing and the
        exclamation mark). If not, you will have to pay £100 instead of
        the standard £10.
        '''
        return "Happy Birthday!"

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
        return self.chance_policy.compute()

    def property_offered_for_auction(self, game_state, player, property):
        '''
        Called when a property is put up for auction.

        Properties are auctioned when a player lands on an unowned square but does
        not want to buy it. All players take part in the auction, including the
        player who landed on the square.

        The property will be sold to the highest bidder using the eBay rule,
        ie, for £1 more than the second-highest bid.

        Return the amount you bid. To put in a bid this must be a positive integer.
        Zero means that you are not bidding (it does not mean that you are bidding
        zero).

        The default behaviour is not to bid.
        '''
        return self.property_policy.acquire_through_auction(game_state,player,property)

    def auction_result(self, status, property, player, amount_paid):
        '''
        Called with the result of an auction. All players receive
        this notification.

        status is either AUCTION_SUCCEEDED or AUCTION_FAILED.

        If the auction succeeded, the property, the player who won
        the auction and the amount they paid are passed to the AI.

        If the auction failed, the player will be None and the
        amount paid will be 0.

        No response is required.
        '''
        if status == PlayerAIBase.Action.AUCTION_SUCCEEDED:
            self.auction_memory.add_auction(property,player,amount_paid)
        pass

    def build_houses(self, game_state, player):
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
        return self.house_policy.compute(game_state, player)

    def sell_houses(self, game_state, player):
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
        if self.needed_money > 0:
            return self.selling_policy.computeHouse(game_state,player)
        return []

    def mortgage_properties(self, game_state, player):
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
        if self.needed_money > 0:
            return self.selling_policy.computeMortgage(game_state,player)
        return []

    def unmortgage_properties(self, game_state, player):
        '''
        Called near the start of the player's turn to give them the
        opportunity to unmortgage properties.

        Unmortgaging costs half the face value plus 10%. Between deciding
        to unmortgage and money being taken the player will be given the
        opportunity to make deals or sell other properties. If after this
        they do not have enough money, the whole transaction will be aborted,
        and no properties will be unmortgaged and no money taken.

        Return a list of property names to unmortgage, like:
        [old_kent_road, bow_street]

        The properties should be Property objects.

        The default is to return an empty list, ie to do nothing.
        '''
        return self.property_policy.acquire_through_unmortgage(game_state,player)

    def get_out_of_jail(self, game_state, player):
        '''
        Called in the player's turn, before the dice are rolled, if the player
        is in jail.

        There are three possible return values:
        PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL
        PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
        PlayerAIBase.Action.STAY_IN_JAIL

        Buying your way out of jail will cost £50.

        The default action is STAY_IN_JAIL.
        '''
        return self.jail_policy.compute(self,game_state,player)

    def propose_deal(self, game_state, player):
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
        if self.needed_money > 0:
            return self.selling_policy.propose_deal(game_state,player)
        return self.property_policy.acquire_through_deal_proposal(game_state,player,player.state.cash - self.money_to_be_taken)

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when another player proposes a deal to you.

        See propose_deal (above) for details of the DealProposal object.

        Return a DealResponse object.

        To reject a deal:
            return DealResponse(DealResponse.Action.REJECT)

        To accept a deal:
            return DealResponse(DealResponse.Action.ACCEPT, maximum_cash_offered=300)
            or
            return DealResponse(DealResponse.Action.ACCEPT, minimum_cash_wanted=800)

        The default is to reject the deal.
        '''
        return self.property_policy.acquire_through_deal_being_proposed(game_state,player,deal_proposal)

    def deal_result(self, deal_info):
        '''
        Called when a proposed deal has finished. The players involved in
        the deal receive this notification.

        deal_info is a PlayerAIBase.DealInfo 'enum' giving indicating
        whether the deal succeeded, and if not why not.

        No response is required.
        '''
        pass

    def deal_completed(self, deal_result):
        '''
        Called when a deal has successfully completed to let all
        players know the details of the deal which took place.

        deal_result is a DealResult object.

        Note that the cash_transferred_from_proposer_to_proposee in
        the deal_result can be negative if cash was transferred from
        the proposee to the proposer.

        No response is required.
        '''
        self.deal_memory.add_deal(deal_result)
        pass

    def player_went_bankrupt(self, player):
        '''
        Called when a player goes bankrupt.

        All non-bankrupt players receive this notification.

        player is a Player object.

        No response is required.
        '''
        if player.name == self.get_name() and player.net_worth + player.state.cash > 0:
            property_net_worth = 0
            property_with_house = 0
            property_unmortgaged = 0
            houses = 0
            for property in player.state.properties:
                # We add the mortgage value of properties...
                if property.is_mortgaged == False:
                    property_unmortgaged += 1
                    property_net_worth += property.mortgage_value

                # We add the resale value of houses...
                if type(property) == Street:
                    if property.number_of_houses > 0:
                        property_with_house += 1
                        houses += property.number_of_houses
                        property_net_worth += int(property.house_price/2 * property.number_of_houses)

            if property_unmortgaged > 0 or property_with_house > 0 or houses > 0:
                Logger.log(player.name + " went bankrupt with a cash of " + format(player.state.cash) + " and a net of " + format(player.net_worth) + "/" + format(property_net_worth), Logger.ERROR)
                Logger.log(player.name + " went bankrupt with " + format(property_unmortgaged) + " properties unmortgaged", Logger.ERROR)
                Logger.log(player.name + " went bankrupt with " + format(property_with_house) + " properties with house", Logger.ERROR)
                Logger.log(player.name + " went bankrupt with " + format(houses) + " houses", Logger.ERROR)
                for property in player.state.properties:
                    # We add the mortgage value of properties...
                    if property.is_mortgaged == False:
                        Logger.log(player.name + "      unmortgage property: " + property.name, Logger.ERROR)

                    # We add the resale value of houses...
                    if type(property) == Street:
                        if property.number_of_houses > 0:
                            Logger.log(player.name + "      housed property: " + property.name + " / " + format(property.number_of_houses), Logger.ERROR)
                #exit(-1)
        pass

    def player_ran_out_of_time(self, player):
        '''
        Called when a player is removed from the game because
        they ran out of processing time.

        All non-bankrupt players receive this notification.

        player is a Player object.

        No response is required.
        '''
        pass

    def game_over(self, winner, maximum_rounds_played):
        '''
        Called when the game is over.

        All players receive this notification.

        winner is the winning player (a Player object) or None if the
        game was drawn.

        maximum_rounds_played is True if the game went to the round-limit.

        No response is required.
        '''
        pass

    def ai_error(self, message):
        '''
        Called if the return value from any of the Player AI functions
        was invalid. for example, if it was not of the expected type.

        No response is required.
        '''
        pass

