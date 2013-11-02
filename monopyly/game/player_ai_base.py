from ..cards.ten_pound_fine_or_take_a_chance import TenPoundFineOrTakeAChance


class PlayerAIBase(object):
    '''
    A base class for player AIs.

    Contains default implementations events that players can be
    notified about. Some events will require a decision from the
    AI. Others are just notifications that something has
    occurred.

    Many of the functions are passed game_state and player_state.

    game_state: A copy of the GameState object, including the
                state of all players. Note that some information
                about other players will be 'redacted', such as
                how much money they have.

    player_state: A copy of the AI's own PlayerState object. Each
                  player has a number, so the AI can tell which of
                  the game players it is.

    These objects are passed as copies to avoid the AIs being able
    to directly change the state.
    '''

    class Action(object):
        '''
        An 'enum' for the various actions an AI can perform.
        '''
        BUY = 0
        DO_NOT_BUY = 1

    def start_of_game(self, player_number):
        '''
        Called at the start of the game to tell each AI
        which player-number it is.

        No response is required.
        '''
        pass

    def start_of_turn(self, game_state, player_number):
        '''
        Called when an AI's turn starts. All AIs receive this notification.

        No response is required.
        '''
        pass

    def player_landed_on_square(self, game_state, square_name, player_number):
        '''
        Called when a player lands on a square. All AIs receive this notification.
        '''
        pass

    def landed_on_unowned_property(self, game_state, player_state, property_name, price):
        '''
        Called when the AI lands on an unowned property. Only the active
        player receives this notification.

        Must return either the BUY or DO_NOT_BUY action from the
        PlayerAIBase.Action enum.

        The default behaviour is DO_NOT_BUY.
        '''
        return PlayerAIBase.Action.DO_NOT_BUY

    def money_will_be_taken(self, player_state, amount):
        '''
        Called shortly before money will be taken from the player.

        Before the money is taken, there will be an opportunity to
        make deals and/or mortgage properties. (This will be done via
        subsequent callbacks.)

        No response is required.
        '''
        pass

    def money_taken(self, player_state, amount):
        '''
        Called when money has been taken from the player.

        No response is required.
        '''
        pass

    def money_given(self, player_state, amount):
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

    def pay_ten_pounds_or_take_a_chance(self):
        '''
        Called when the player picks up the "Pay a £10 fine or take a Chance" card.

        Return either:
            TenPoundFineOrTakeAChance.Action.PAY_TEN_POUND_FINE
            or
            TenPoundFineOrTakeAChance.Action.TAKE_A_CHANCE
        '''
        # TODO: move this action to this class
        return TenPoundFineOrTakeAChance.Action.PAY_TEN_POUND_FINE

    def property_offered_for_auction(self, game_state, player_state, property_name, face_value):
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

    def build_houses(self, game_state, player_state):
        '''
        Called near the start of the player's turn to give the option of building houses.

        Return a list of tuples indicating which properties you want to build houses
        on and how many houses to build on each. For example:
        [(Square.Name.PARK_LANE, 3), (Square.Name.MAYFAIR, 4)]

        Return an empty list if you do not want to build.

        Notes:
        - You must own a whole set of unmortgaged properties before you can
          build houses on it.

        - You can build on multiple sets in one turn. Just specify all the streets
          and houses you want to build.

        - Build five houses on a property to have a "hotel".

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

    def mortgage_properties(self, game_state, player_state):
        '''
        Gives the player an option to mortgage properties.

        This is called before any debt is paid (house building, rent,
        tax, fines from cards etc).

        Notes:
        - You receive half the face value of each property mortgaged.

        - You cannot mortgage properties with houses on them.
          (The AI will have been given the option to sell houses before this
          function is called.)

        Return a list of property names to mortgage, for example:
        [Square.Name.BOW_STREET, Square.Name.LIVERPOOL_STREET_STATION]

        Return an empty list if you do not want to mortgage anything.

        The default behaviour is not to mortgage anything.
        '''
        return []

