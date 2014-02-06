__author__ = 'brett'

from monopyly import *
from monopyly.utility import Logger
from monopyly.game.board import Board
from monopyly.squares.property import Property
from monopyly.squares.property_set import PropertySet
from monopyly.squares.station import Station
from monopyly.squares.street import Street
from monopyly.squares.utility import Utility

import random

DONT_BID_ON_AUCTIONS_WITH_MORTAGED_PROPS = True
PROPOSE_DEALS = True

#PROBABILITY_SQUARE_LANDING_FACTOR = 0.14
PROBABILITY_SQUARE_LANDING_FACTOR_MAX = 0.14
PROBABILITY_SQUARE_LANDING_FACTOR_MIN = 0.09

PROBS_TO_12 = [
    0.0, 
    0.0,
    1.0 / 36.0, # 2
    2.0 / 36.0, # 3
    3.0 / 36.0, # 4
    4.0 / 36.0, # 5
    5.0 / 36.0, # 6
    6.0 / 36.0, # 7
    5.0 / 36.0, # 8
    4.0 / 36.0, # 9
    3.0 / 36.0, # 10
    2.0 / 36.0, # 11
    1.0 / 36.0, # 12
    ]

PROBS_TO_40 = [
    0.00000000000000, # 0
    0.00000000000000, # 1
    0.02777777777778, # 2
    0.05555555555556, # 3
    0.08410493827160, # 4
    0.11419753086420, # 5
    0.14662637174211, # 6
    0.18222736625514, # 7
    0.16634575998323, # 8
    0.15552602499619, # 9
    0.14778379568769, # 10
    0.14127531398711, # 11
    0.13419944115166, # 12
    0.12470357532339, # 13
    0.13856733998588, # 14
    0.14577135028207, # 15
    0.14835462718374, # 16
    0.14788998341445, # 17
    0.14567233892515, # 18
    0.14288627461097, # 19
    0.14076409441802, # 20
    0.14074487228672, # 21
    0.14155829388956, # 22
    0.14250305429015, # 23
    0.14324317122435, # 24
    0.14364991042100, # 25
    0.14367048113225, # 26
    0.14320718896912, # 27
    0.14276360881384, # 28
    0.14252805073293, # 29
    0.14251476065809, # 30
    0.14265180184901, # 31
    0.14283608629366, # 32
    0.14297143339436, # 33
    0.14300286989638, # 34
    0.14295935994681, # 35
    0.14288901516830, # 36
    0.14282995685566, # 37
    0.14280152812847, # 38
    0.14280577338958, # 39
    0.14283223633606, # 40
    ]

HOUSE_PROP_SET_SELL_ORDER = [
    PropertySet.BROWN,
    PropertySet.DARK_BLUE,
    PropertySet.LIGHT_BLUE,
    PropertySet.PURPLE,
    PropertySet.GREEN,
    PropertySet.YELLOW,
    PropertySet.ORANGE,
    PropertySet.RED,
    ]

class BrettAI(PlayerAIBase):


    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.cash_reserve = 0
        self.high_water_mark = 0
        self.num_turns = 0
        self.num_get_out_of_jail_cards = 0

        self.propose_deal_turn_min = 10
        self.propose_deal_turn_max = 500

    def get_name(self):
        '''
        Returns the name shown for this AI.
        '''
        return "Bretts AI"

    def start_of_game(self):
        '''
        Called at the start of the game.

        No response is required.
        '''
        Logger.log("# Start of Game.", Logger.INFO)
        self.num_turns = 0
        self.num_get_out_of_jail_cards = 0
        self.amount_to_raise = 0.0
        self.mortgaged_properties = []

        return

    def start_of_turn(self, game_state, player):
        '''
        Called when an AI's turn starts. All AIs receive this notification.

        No response is required.
        '''
        if player.ai != self:
            return

        self.num_turns += 1

        self.turn_properties_in_deal = set()

        ( self.cash_reserve, self.high_water_mark) = self._calc_cash_reserve(game_state, player)

        self.amount_to_raise = 0.0


        Logger.log("# Start of Turn {0} - cash_reserve = {1}, HWM = {2}.".format(self.num_turns, self.cash_reserve, self.high_water_mark), Logger.INFO)

        return

    def player_landed_on_square(self, game_state, square, player):
        '''
        Called when a player lands on a square. All AIs receive this notification.

        No response is required.
        '''
        if player.ai != self:
            return

        Logger.log("# Landed on Square {0}".format(square), Logger.INFO)
        return


    def landed_on_unowned_property(self, game_state, player, property):
        '''
        price the property / evaluate the risks of buying
        '''
        ret = PlayerAIBase.Action.DO_NOT_BUY
        act = "not buying"
        if player.state.cash > (self.cash_reserve + property.price):
            ret = PlayerAIBase.Action.BUY
            act = "buying"

        Logger.log("# Landed on unowned property and {0}".format(act), Logger.INFO)
        return ret

    def money_will_be_taken(self, player, amount):
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.

        if amount > player.state.cash:
          sell stuff
        '''
        if amount >= player.state.cash:
            self.amount_to_raise = amount - player.state.cash + 1

        Logger.log("# Money will be taken and amount to raise = {0}".format(self.amount_to_raise), Logger.INFO)

        return

    def money_taken(self, player, amount):
        '''
        Called when money has been taken from the player.

        No response is required.
        '''
        Logger.log("# Money taken : {0}".format(amount), Logger.INFO)
        return

    def got_get_out_of_jail_free_card(self):
        '''
        Called when the player has picked up a
        Get Out Of Jail Free card.

        No response is required.

        TODO: increment get_out_of_jail counter
        '''
        self.num_get_out_of_jail_cards += 1
        return

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
        if self.amount_to_raise > 0:
            # If we are selling stuff, take a chance!
            # or if we have lots of cash
            return PlayerAIBase.Action.TAKE_A_CHANCE

        if player.state.cash > self.high_water_mark + 500:
            return PlayerAIBase.Action.TAKE_A_CHANCE

        return PlayerAIBase.Action.PAY_TEN_POUND_FINE


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

        if player.ai is not self:
            Logger.log("# !!! ERROR player is NOT me in property_offered_for_auction")

        if self.amount_to_raise > 0.0:
            return 0.0

        if len(self.mortgaged_properties) > 0 and DONT_BID_ON_AUCTIONS_WITH_MORTAGED_PROPS:
            return 0

        price_to_bid = 0.0
        (bid_price, ask_price) = self._calc_value_of_properties(game_state, player, [ property ])
        if player.state.cash > bid_price + self.cash_reserve:
            price_to_bid = bid_price
        
        Logger.log("# Property being auctioned and bidding {0}".format(price_to_bid), Logger.INFO)

        return price_to_bid

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
            Logger.log("# Property won at auction", Logger.INFO)
        else:
            Logger.log("# Property lost at auction", Logger.INFO)

        return

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
        if self.amount_to_raise > 0.0:
            return []

        if len(self.mortgaged_properties) > 0:
            return []

        # We find the first set we own that we can build on...
        houses_to_build = []
        for owned_set in player.state.owned_unmortgaged_sets:
            # We can't build on stations or utilities, or if the
            # set already has hotels on all the properties...
            if not owned_set.can_build_houses:
                continue

            # We see how much money we need for one house on each property...
            cost = owned_set.house_price * owned_set.number_of_properties
            if player.state.cash > (self.cash_reserve + cost):
                # We build one house on each property...
                houses_to_build = [(p, 1) for p in owned_set.properties]
                break

        Logger.log("# Building the following houses: {0}".format(str(houses_to_build)), Logger.INFO)

        return houses_to_build

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
        houses_to_sell = []
        if self.amount_to_raise > 0.0:
            money_generated = 0

            for prop_set in HOUSE_PROP_SET_SELL_ORDER:
                (num_houses, owned_prop_list) = self._get_owned_houses_in_property_set(game_state, player, prop_set)
                num_house_list = [ 0 for p in owned_prop_list ]
                houses_sold = 0
                while num_houses < houses_sold and money_generated < self.amount_to_raise:
                    for i in range(0, len(owned_prop_list)):
                        if num_house_list[i] < owned_prop_list[i].number_of_houses:
                            num_house_list[i] += 1
                            houses_sold += 1
                            money_generated += int(owned_prop_list[i].house_price / 2)
                if houses_sold > 0:
                    for i in range(0, len(owned_prop_list)):
                        if num_house_list[i] > 0:
                            houses_to_sell.append( (owned_prop_list[i], num_house_list[i], ))


            # update amount_to_raise
            self.amount_to_raise -= money_generated
            if self.amount_to_raise < 0:
                self.amount_to_raise = 0.0

        if len(houses_to_sell) > 0:
            Logger.log("# Selling the following houses: {0}".format(str(houses_to_sell)), Logger.INFO)
            
        return houses_to_sell

    def _get_owned_houses_in_property_set(self, game_state, player, set_enum):
        board = game_state.board
        props = board.get_properties_for_set(set_enum)
        owned_prop_list = []
        num_houses = 0
        for p in props:
            if p.owner == player and p.number_of_houses > 0:
                owned_prop_list.append(p)
                num_houses += p.number_of_houses
        return (num_houses, owned_prop_list)
              


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
        properties_to_mortage = []
        if self.amount_to_raise > 0.0:
            money_generated = 0
            board = game_state.board
            for sq in board.squares:
                if isinstance(sq, Property) and sq.owner == player and sq.is_mortgaged == False:
                    money_generated += int(sq.price / 2)
                    properties_to_mortage.append(sq)

                    if money_generated > self.amount_to_raise:
                        break
            self.amount_to_raise -= money_generated
            if self.amount_to_raise < 0.0:
                self.amount_to_raise = 0.0

        if len(properties_to_mortage) > 0:
            Logger.log("# Mortgaging the following properties: {0}".format(str(properties_to_mortage)), Logger.INFO)
            self.mortgaged_properties.extend(properties_to_mortage)
            
        return properties_to_mortage

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
        props_to_unmortgage = []
        if len(self.mortgaged_properties) > 0:
            cash_to_spend = player.state.cash - self.cash_reserve
            mortgaged = sorted(self.mortgaged_properties, key = lambda p: p.price)
            while cash_to_spend > 0.0 and len(mortgaged) > 0:
                mc = int(mortgaged[0].price * 0.5)
                cash_to_spend -= mc
                if cash_to_spend >= 0.0:
                    props_to_unmortgage.append(mortgaged[0])
                    mortgaged.pop(0)
            Logger.log("# Unmortgaging: {0}".format(str(props_to_unmortgage)), Logger.INFO)
        for i in range(0, len(props_to_unmortgage)):
            self.mortgaged_properties.remove(props_to_unmortgage[i])
        return props_to_unmortgage

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
        if self._count_unowned_property(game_state) >= 8:
            if self.num_get_out_of_jail_cards > 0:
                self.num_get_out_of_jail_cards -= 1
                return PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD
            elif player.state.cash > self.high_water_mark:
                return PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL

        return PlayerAIBase.Action.STAY_IN_JAIL


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

        if not PROPOSE_DEALS:
            return None

        if self.num_turns < self.propose_deal_turn_min or self.num_turns > self.propose_deal_turn_max:
            return None

        # TODO Potentially sell stuff if we need to
        if self.amount_to_raise > 0.0:
            return None

        if len(self.mortgaged_properties) > 0:
            return None

        properties_we_like = []
        if len(player.state.properties) == 0:
            # hell, we'll bid on anything!
            board = game_state.board
            for sq in board.squares:
                if isinstance(sq, Property) and sq.owner is not None and sq.owner != player:
                    properties_we_like.append(sq.name)
        else:

            # OK, pick out some good properties to bid on
            properties_we_like = set()
            for p in player.state.properties:
                properties_we_like.update(p.property_set.properties)

            properties_we_like = [ p.name for p in properties_we_like ]

        Logger.log("# Propose deal called!", Logger.INFO)

        deal_proposal = DealProposal()

        random.shuffle(properties_we_like)

        # We check to see if any of the properties we like is owned
        # by another player...
        for property_name in properties_we_like:
            property = game_state.board.get_square_by_name(property_name)
            if (property.owner is player or property.owner is None):
                # The property is either not owned, or owned by us...
                continue

            if property_name in self.turn_properties_in_deal:
                continue

            # The property is owned by another player, so we make them an
            # offer for it...
            (bid_price, ask_price) = self._calc_value_of_properties(game_state, player, [ property ])

            price_offered = bid_price
            if player.state.cash  > price_offered + self.high_water_mark:
                self.turn_properties_in_deal.add(property_name)

                return DealProposal(
                    properties_wanted=[property],
                    maximum_cash_offered=price_offered,
                    propose_to_player=property.owner)

        return None

    def deal_proposed(self, game_state, player, deal_proposal):
        '''
        Called when a deal is proposed by another player.
        '''


        if len(deal_proposal.properties_wanted) > 0 and len(deal_proposal.properties_offered) == 0:
            (bid_price, ask_price) = self._calc_value_of_properties(game_state, player, deal_proposal.properties_wanted)

            if ask_price < self.amount_to_raise:
                ask_price = self.amount_to_raise

            Logger.log("# Accepted proposed deal of wanted properties {0} for {1}".format(str(deal_proposal.properties_wanted), ask_price))
            return DealResponse(
                action=DealResponse.Action.ACCEPT,
                minimum_cash_wanted = ask_price
                )

        if self.amount_to_raise > 0.0:
            return DealResponse(DealResponse.Action.REJECT)

        # We only accept deals for single properties wanted from us...
        if len(deal_proposal.properties_offered) > 0 and len(deal_proposal.properties_wanted) == 0:
            (bid_price, ask_price) = self._calc_value_of_properties(game_state, player, deal_proposal.properties_offered)
            if player.state.cash > bid_price + self.high_water_mark:
                Logger.log("# Accepted proposed deal of offered properties {0} for {1}".format(str(deal_proposal.properties_offered), bid_price))
                return DealResponse(
                    action=DealResponse.Action.ACCEPT,
                    maximum_cash_offered = bid_price
                    )



        return DealResponse(DealResponse.Action.REJECT)

    def deal_result(self, deal_info):
        '''
        Called when a proposed deal has finished. The players involved in
        the deal receive this notification.

        deal_info is a PlayerAIBase.DealInfo 'enum' giving indicating
        whether the deal succeeded, and if not why not.

        No response is required.
        '''
        return

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
        pass

    def property_offered_for_auction(self, game_state, player, property):
        if self.amount_to_raise > 0.0:
            return 0

        (bid_price, ask_price) = self._calc_value_of_properties(game_state, player, [ property ])
        if bid_price < self.high_water_mark:
            if bid_price >= self.cash_reserve:
                bid_price = (self.high_water_mark - self.cash_reserve)
            else:
                bid_price = 0

        return bid_price

    def players_birthday(self):
        return "Happy Birthday!"

    def _calc_cash_reserve(self, game_state, player):
        # OK, what we want to do is calculate how much cash to keep in
        # reserve here This is currently enough to fund one turn
        # around the board from our current position.

        # We calculate this by taking the cost of each square * the
        # probability of landing on the square

        # if we are before the "Go to Jail" square, we factor in the
        # probability of 1 trip to jail

        # There is also the probability of getting a bad card from
        # Chance, which is higher at the start of the game, but
        # decreases throughout the game.

        go_to_jail_index = game_state.board.get_index(Square.Name.GO_TO_JAIL)
        reserve = 0.0
        rents_times_probs = 0.0
        num_owned_properties = 0
        num_owned_stations = 0
        num_owned_utilities = 0
        jail_reserve = 0.0

        ## 

        ( rents_times_probs, chance_penalty, all_rents, go_to_jail_prob, tax_penalty ) = \
            self._calc_expected_cost_of_turn(game_state, player)
        
        ##
        max_cash_reserve_buffer = 100
        cash_reserve_buffer = self.num_turns * 10
        if cash_reserve_buffer > max_cash_reserve_buffer:
            cash_reserve_buffer = max_cash_reserve_buffer

        cash_reserve = int(rents_times_probs + chance_penalty + (go_to_jail_prob * 50.0) + tax_penalty) + cash_reserve_buffer

        max_hwm_buffer = 500
        hwm_buffer = self.num_turns * 10 + len(all_rents) * 20
        if hwm_buffer > max_hwm_buffer:
            hwm_buffer = max_hwm_buffer

        high_water_mark = int(rents_times_probs + chance_penalty + (go_to_jail_prob * 50.0) + tax_penalty) + hwm_buffer

        all_rents.sort(reverse = True)
        if len(all_rents) > 0:
            highest_rent = all_rents[0] + hwm_buffer
            if high_water_mark < highest_rent:
                high_water_mark = highest_rent

        return ( cash_reserve, high_water_mark )
        

    def _old_calc_cash_reserve(self, game_state, player):

        all_rents = []

        for bd in range(0, Board.NUMBER_OF_SQUARES):
            sq = game_state.board.squares[bd]
            if isinstance(sq, Street):
                if sq.owner is not None and sq.owner is not self:
                    num_owned_properties += 1

                    # calculate the current rent
                    rent = sq.calculate_rent(None, player)

                    all_rents.append(rent)

                    # should maybe calculate the rent with 1 more house added...
                    Logger.log("Got rent of {0}".format(rent))
                    rent_prob = (rent * PROBS_TO_40[bd])
                    rents_times_probs += rent_prob
                    if bd > player.state.square + 2:
                        reserve += rent_prob

                        if player.state.square < go_to_jail_index:
                            jail_reserve += (0.15 * rent_prob)

            elif isinstance(sq, Station):
                if sq.owner is not None and sq.owner is not self:
                    num_owned_stations += 1

                    # calculate the current rent
                    rent = self._calc_rent_on_station(game_state, sq)

                    all_rents.append(rent)

                    # should maybe calculate the rent with 1 more house added...
                    Logger.log("Got station rent of {0}".format(rent))
                    rent_prob = (rent * PROBS_TO_40[bd])
                    rents_times_probs += rent_prob
                    if bd > player.state.square + 2:
                        reserve += rent_prob

                        if player.state.square < go_to_jail_index:
                            jail_reserve += (0.15 * rent_prob)

            elif isinstance(sq, Utility):
                if sq.owner is not None and sq.owner is not self:
                    num_owned_utilities += 1

                    # calculate the current rent
                    rent = self._calc_prob_rent_on_utility(game_state, sq)

                    all_rents.append(rent)

                    # should maybe calculate the rent with 1 more house added...
                    Logger.log("Got utility rent of {0}".format(rent))
                    rent_prob = (rent * PROBS_TO_40[bd])
                    rents_times_probs += rent_prob
                    if bd > player.state.square + 2:
                        reserve += rent_prob

                        if player.state.square < go_to_jail_index:
                            jail_reserve += (0.15 * rent_prob)
            elif isinstance(sq, Chance):
                chance_penalty = self._calc_chance_penalty(player)
                Logger.log("# calculated chance_penalty of {0}".format(chance_penalty))
                reserve += chance_penalty
        Logger.log("# calculated reserve of {0}, jail reserve = {1}".format(reserve, jail_reserve))

        all_rents.sort(reverse = True)

        top_rents_sum = 0
        for i in range(0, 6):
            if len(all_rents) > i:
                top_rents_sum += all_rents[i]
        Logger.log("# top_rents_sum = {0}".format(top_rents_sum))

        reserve += jail_reserve
        reserve += 30.0
        reserve = round(reserve)

        if top_rents_sum > reserve and top_rents_sum < 1000.0:
            reserve = top_rents_sum

        Logger.log("# Using reserve of {0}".format(reserve))

        return reserve

    def _calc_rent_on_station(self, game_state, station):
        board = game_state.board
        owned_stations = board.get_property_set(PropertySet.STATION).intersection(station.owner.state.properties)
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

    def _calc_prob_rent_on_utility(self, game_state, uty):
        board = game_state.board
        owned_utilities = board.get_property_set(PropertySet.UTILITY).intersection(uty.owner.state.properties)
        number_of_owned_utilities = len(owned_utilities)

        rent = 0.0
        if number_of_owned_utilities == 1:
            for i in range(2, len(PROBS_TO_12)):
                rent += (PROBS_TO_12[i] * 4)
        elif number_of_owned_utilities == 2:
            for i in range(2, len(PROBS_TO_12)):
                rent += (PROBS_TO_12[i] * 10)

        return rent

    def _calc_chance_penalty(self, player):
        num_houses = 0
        for p in player.state.properties:
            if isinstance(p, Street):
                num_houses = p.number_of_houses
        
        penalty = 0.0
        penalty += (1.0 / 16.0) * num_houses * 25.0
        penalty += (1.0 / 16.0) * 15.0
        penalty += (1.0 / 16.0) * 20.0
        penalty += (1.0 / 16.0) * 150.0

        return penalty

    def _calc_expected_cost_of_turn(self, game_state, player):
        cur_square = player.state.square

        rents_times_probs = 0.0
        chance_penalty = 0.0
        tax_penalty = 0.0
        go_to_jail_prob = 0.0
        all_rents = []

        for dice_roll in range(0, len(PROBS_TO_12)):
            bd = player.state.square + dice_roll
            if bd >= Board.NUMBER_OF_SQUARES:
                bd -= Board.NUMBER_OF_SQUARES

            sq = game_state.board.squares[bd]
            if sq.name == Square.Name.GO_TO_JAIL:
                go_to_jail_prob = PROBS_TO_12[dice_roll]
            elif isinstance(sq, Street):
                if sq.owner is not None and sq.owner != player:
                    # calculate the current rent
                    rent = sq.calculate_rent(None, player)

                    all_rents.append(rent)

                    # should maybe calculate the rent with 1 more house added...
                    rent_prob = (rent * PROBS_TO_12[dice_roll])
                    rents_times_probs += rent_prob

            elif isinstance(sq, Station):
                if sq.owner is not None and sq.owner != player:
                    # calculate the current rent
                    rent = self._calc_rent_on_station(game_state, sq)

                    all_rents.append(rent)

                    rent_prob = (rent * PROBS_TO_12[dice_roll])
                    rents_times_probs += rent_prob

            elif isinstance(sq, Utility):
                if sq.owner is not None and sq.owner != player:
                    # calculate the current rent
                    rent = self._calc_prob_rent_on_utility(game_state, sq)

                    all_rents.append(rent)

                    rent_prob = (rent * PROBS_TO_12[dice_roll])
                    rents_times_probs += rent_prob
            elif isinstance(sq, Chance):
                chance_penalty += self._calc_chance_penalty(player)
            elif isinstance(sq, Tax):
                tax_penalty += (sq.tax * PROBS_TO_12[dice_roll])

        return ( rents_times_probs, chance_penalty, all_rents, go_to_jail_prob, tax_penalty )


    def _calc_value_of_properties(self, game_state, player, properties):
        # The value of the street is (roughly)
        # the number of players * expected_future_rent - expected_future_cost

        max_rent = 0.0
        min_rent = 0.0
        price = 0.0
        house_price_cost = 0.0

        min_value = 0.0

        for sq in properties:
            price += sq.price
            min_value += sq.mortgage_value

            num_props_owned = 0
            for op in sq.property_set.properties:
                if op.owner is not None and op.owner == player:
                    num_props_owned += 1

            prob_building = 0.1
            if num_props_owned > 0:
                prob_building = (0.20 * num_props_owned)

            if self.num_turns > 300:
                prob_building *= float(self.num_turns / 500.0)

            if isinstance(sq, Street):
                if len(sq.rents) > 0:
                    top_rent = sq.rents[len(sq.rents)-1]
                    max_rent += (sq.rents[0] + ((top_rent - sq.rents[0]) * prob_building))
                    min_rent += sq.rents[0]

                house_price_cost += (sq.house_price * ((5 - sq.number_of_houses) * prob_building))
                min_value += int(sq.house_price/2 * sq.number_of_houses)


            elif isinstance(sq, Utility):
                min_rent += 4.0
                max_rent += (4.0 + (6.0 * prob_building))
            elif isinstance(sq, Station):
                min_rent += 25.0
                max_rent += (25 + (175.0 * prob_building))

        remaining_turns = 500 - self.num_turns
        if remaining_turns < 0:
            # this shouldn't happen!
            remaining_turns = -remaining_turns

        # no houses
        min_expected_value = remaining_turns * (len(game_state.players)-1) * min_rent * PROBABILITY_SQUARE_LANDING_FACTOR_MIN

        max_expected_value = remaining_turns * (len(game_state.players)-1) * max_rent * PROBABILITY_SQUARE_LANDING_FACTOR_MAX - house_price_cost
        if max_expected_value < min_expected_value:
            max_expected_value = min_expected_value

        expected_value = (min_expected_value + max_expected_value) / 2.0

        factor = float(remaining_turns / 500.0)

        fair_price = (expected_value * factor) + (min_value * (1.0 - factor))

        Logger.log("### (minp, maxp, fair, min) = ({0}, {1}, {2}, {3})".format(min_expected_value, max_expected_value, fair_price, min_value), Logger.INFO)

        bid_price = min_expected_value
        ask_price = max_expected_value

        if bid_price < min_value:
            bid_price = min_value + 10
        
        if ask_price < min_value:
            ask_price = min_value * 2.0

        bid_price = int(bid_price)
        ask_price = int(ask_price)

        Logger.log("*** Calculated value for {0} properties of {1}, {2}".format(len(properties), bid_price, ask_price))
        return (bid_price, ask_price)

    def _count_unowned_property(self, game_state):
        board = game_state.board
        count = 0
        for sq in board.squares:
            if isinstance(sq, Property) and sq.owner is None:
                count += 1
        return count

    def player_went_bankrupt(self, player):
        Logger.log("# Player {0} went bankrupt at turn {1}".format(player.name, self.num_turns), Logger.INFO)
        return

    def game_over(self, winner, maximum_rounds_played):
        Logger.log("# GAME OVER at turn {0}".format(self.num_turns), Logger.INFO)
