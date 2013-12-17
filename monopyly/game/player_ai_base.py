from .deal_proposal import DealProposal
from .deal_response import DealResponse


class PlayerAIBase(object):
    '''
    A base class for player AIs.

    Contains default implementations events that players can be
    notified about. Some events will require a decision from the
    AI. Others are just notifications that something has
    occurred.

    Many of the functions are passed game_state and player.

    game_state: The GameState object, including the state of all players
                and the board.

    player:     The Player object for the current player, ie "you".

    "Cheating"
    ----------
    AIs must not change the state of the game except through the interactions defined by
    the PlayerAIBase API. This includes, but is not limited to:
    - Changing the cash or properties owned by any player
    - Changing the state of the board or the Chance or Community Chest cards
    - Setting the random seed used by the dice
    - 'Stealing' CPU from other players by running extra threads.
    You know what I mean: No 'Kobayashi Maru' style cheating!

    AIs must not deliberately act favourably towards other specific AIs.
    You may enter multiple AIs into the competition, but you are not allowed to
    create 'sacrificial' AIs which deliberately boost other AIs chances of winning.

    You are allowed to remember details about other players' behaviour between
    games. Only one instance of your AI is created for the whole tournament and is
    reused for each game. So if you want, you can learn how other AIs behave and use
    that information in subsequent games.
    '''

    class Action(object):
        '''
        An 'enum' for the various actions an AI can perform, and
        info passed to them.
        '''
        # Buying houses...
        BUY = 0
        DO_NOT_BUY = 1

        # Pay a £10 or take a Chance...
        PAY_TEN_POUND_FINE = 2
        TAKE_A_CHANCE = 3

        # Getting out of jail...
        BUY_WAY_OUT_OF_JAIL = 4
        PLAY_GET_OUT_OF_JAIL_FREE_CARD = 5
        STAY_IN_JAIL = 6

        # Auctioning...
        AUCTION_SUCCEEDED = 7
        AUCTION_FAILED = 8

    class DealInfo(object):
        '''
        An 'enum' for the various outcomes from a deal.
        '''
        SUCCEEDED = 0
        INVALID_DEAL_PROPOSED = 1
        ASKED_FOR_TOO_MUCH_MONEY = 2
        OFFERED_TOO_LITTLE_MONEY = 3
        PLAYER_DID_NOT_HAVE_ENOUGH_MONEY = 4
        DEAL_REJECTED = 5

    def get_name(self):
        '''
        Returns the name of this AI player.
        '''
        return "no-name"

    def start_of_game(self):
        '''
        Called at the start of the game.

        No response is required.
        '''
        pass

    def start_of_turn(self, game_state, player):
        '''
        Called when an AI's turn starts. All AIs receive this notification.

        No response is required.
        '''
        pass

    def player_landed_on_square(self, game_state, square, player):
        '''
        Called when a player lands on a square. All AIs receive this notification.
        '''
        pass

    def landed_on_unowned_property(self, game_state, player, property):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        return PlayerAIBase.Action.DO_NOT_BUY

    def money_will_be_taken(self, player, amount):
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.
        '''
        pass

    def money_taken(self, player, amount):
        '''
        Called when money has been taken from the player.

        No response is required.
        '''
        pass

    def money_given(self, player, amount):
        '''
        Called when money has been given to the player.

        No response is required.
        '''
        pass

    def got_get_out_of_jail_free_card(self):
        '''
        Called when the player has picked up a
        Get Out Of Jail Free card.

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
        return "I hope you choke on your birthday cake!"

    def pay_ten_pounds_or_take_a_chance(self, game_state, player):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            PlayerAIBase.Action.PAY_TEN_POUND_FINE
            or
            PlayerAIBase.Action.TAKE_A_CHANCE
        '''
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
        return 0

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
        return []

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
        return []

    def get_out_of_jail(self, player):
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
        return None

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
        return DealResponse(DealResponse.Action.REJECT)

    def deal_result(self, deal_info):
        '''
        Called when a proposed deal has finished.

        deal_info is a PlayerAIBase.DealInfo 'enum' giving indicating
        whether the deal succeeded, and if not why not.

        No response is required.
        '''
        pass

    def player_went_bankrupt(self, player):
        '''
        Called when a player goes bankrupt.

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
