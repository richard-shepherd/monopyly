from .dice import Dice
from .player import Player
from .game_state import GameState
from .player_ai_base import PlayerAIBase
from .board import Board
from .deal_response import DealResponse
from .deal_result import DealResult
from ..squares import Square, Property, Street
from ..utility import Logger


class Game(object):
    '''
    Manages one game of monopoly.

    Holds all the game state: the board, the cards and the players.
    It rolls the dice and moves the players. It calls into the player
    AIs when events occur and when there are decisions to be made.

    It keeps track of players' solvency and decides when a player is
    bankrupt and when the game is over.

    There is a turn limit (as otherwise the game could continue forever).
    When the limit is reached, all assets are liquidated (houses sold,
    properties mortgaged) and the winner is the player with the most money.
    '''

    class Action(object):
        '''
        An 'enum' for actions that can happen during the game.
        '''

        # Dice...
        ROLL_AGAIN = 1
        DO_NOT_ROLL_AGAIN = 2

        # Buying and selling properties...
        PROPERTY_BOUGHT = 3
        PROPERTY_NOT_BOUGHT = 4

        # Transferring money between players...
        ROLLBACK_ON_INSUFFICIENT_CASH = 5
        PAY_AS_MUCH_AS_POSSIBLE = 6
        TRANSFER_SUCCEEDED = 7
        TRANSFER_FAILED = 8

        # Winning and losing...
        GAME_OVER = 9
        GAME_NOT_OVER = 10

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.state = GameState()
        self.dice = Dice()
        self.most_recent_total_dice_roll = 0
        self.status = Game.Action.GAME_NOT_OVER

        # The winning player...
        self.winner = None

        # Rounds in the game...
        self.maximum_rounds = 500
        self.number_of_rounds_played = 0

        # True if we are in the make-deals phase...
        self._in_make_deals = False

        # A Tournament object, if the game is part of a tournament.
        # This lets us notify the tournament about game events, which
        # can then be relayed to the GUI...
        self.tournament = None

        # Whether the eminent domain rule is being played.
        # If it is, then all properties are compulsorily purchased
        # and re-auctioned at a specified turn if no houses have
        # been built by that time...
        self.eminent_domain = True
        self.eminent_domain_round = 200

    def add_player(self, ai_info):
        '''
        Adds a player AI.

        The ai_info is a tuple of (ai, player-number)

        Returns the Player object created.
        '''
        # ai_info might be a tuple (ai, player-number) or it
        # might just be an AI...
        try:
            ai = ai_info[0]
            player_number = ai_info[1]
        except:
            ai = ai_info
            player_number = 0

        # We wrap the AI up into a Player object...
        player = Player(ai, player_number, self.state.board)
        self.state.players.append(player)
        return player

    def play_game(self):
        '''
        Plays a game of monopoly.
        '''
        # We tell the players that the game is starting, and which
        # player-number they are...
        Logger.log("Start of game. Players:")
        Logger.indent()
        for player in self.state.players:
            player.call_ai(player.ai.start_of_game)
            Logger.log(player.name)
        Logger.dedent()

        # We play a game...
        while True:
            # We play a round...
            self.play_one_round()
            self.number_of_rounds_played += 1

            # We check if the game is over (ie, only one non-bankrupt
            # player left)...
            self._check_game_status()
            if self.status == Game.Action.GAME_OVER:
                break

            if self.number_of_rounds_played == self.maximum_rounds:
                Logger.log("Maximum rounds played")
                break

        # The game is over, so we work out which player has won...
        self.status = Game.Action.GAME_OVER
        self._find_winner()

    def play_one_round(self):
        '''
        Plays one round of the game, ie one turn for each of
        the players.

        The round can come to an end before all players' turns
        are finished if one of the players wins.

        Returns a Game.Action enum.
        '''

        # We check if we need to play the eminent domain rule...
        self._check_eminent_domain_rule()

        # We play a turn for each player in the game.
        # Note that we iterate over a copy of the list of players, as
        # players can be removed from the game if they go bankrupt.
        list_players = list(self.state.players)
        for player in list_players:
            if player.state.cash < 0:
                # The player is out...
                continue

            # The player takes a turn...
            self.play_one_turn(player)

            # We notify the GUI (via the Tournament object)...
            if self.tournament is not None:
                self.tournament.turn_played(self)

            # If there is only one player left, the game is over...
            if len(self.state.players) == 1:
                break

    def play_one_turn(self, current_player):
        '''
        Plays one turn for one player.
        '''
        # Some logging...
        Logger.log("")
        Logger.log("Start of turn for {0}".format(current_player.name))
        Logger.indent()
        Logger.log("Cash=£{0}, Net Worth=£{1}".format(current_player.state.cash, current_player.net_worth))

        # We keep a count of the number of turns played (for calculating
        # processing time per turn)...
        current_player.state.turns_played += 1

        # We keep a count of how many turns the player has been in jail for...
        if current_player.state.is_in_jail:
            current_player.state.number_of_turns_in_jail += 1

        # We notify all players that this player's turn is starting...
        for player in self.state.players:
            player.call_ai(player.ai.start_of_turn, self.state, current_player)

        # The player can make deals...
        self._make_deals(current_player)

        # If the player is in jail, they have a chance to buy their way out...
        self._get_out_of_jail(current_player)

        # The player can unmortgage properties...
        self._unmortgage_properties(current_player)

        # The player can build houses...
        self._build_houses(current_player)

        # This while loop manages rolling again if the player rolls doubles...
        roll_again = Game.Action.ROLL_AGAIN
        number_of_doubles_rolled = 0
        while roll_again == Game.Action.ROLL_AGAIN:
            roll_again, number_of_doubles_rolled = self.roll_and_move(current_player, number_of_doubles_rolled)

            # We check if the player has gone bankrupt at the end of each move...
            if current_player.state.cash < 0:
                break

        # We show the processing time remaining for the player...
        Logger.log("Processing time remaining={0}sec".format(current_player.state.ai_processing_seconds_remaining))

        # We check if any players went bankrupt during this turn...
        self._check_for_bankrupt_players()

        # We check if the player ran out of time this turn...
        if current_player.state.ai_processing_seconds_remaining <= 0.0:
            self._player_ran_out_of_time(current_player)

        Logger.dedent()

    def roll_and_move(self, current_player, number_of_doubles_rolled):
        '''
        Rolls the dice, moves the player and takes the appropriate
        action for the square landed on.

        Returns whether we should roll again and the number of doubles rolled.
        '''
        # We roll the dice and move the player...
        roll1, roll2 = self.dice.roll()
        self.most_recent_total_dice_roll = roll1 + roll2
        doubles_rolled = (roll1 == roll2)

        # We log the dice roll...
        Logger.log("Rolled ({0}, {1})".format(roll1, roll2))

        # If the player is in jail, we check if they rolled themself out...
        if current_player.state.is_in_jail :
            if not doubles_rolled and current_player.state.number_of_turns_in_jail < 3:
                # They have not rolled doubles, so they stay in jail...
                return Game.Action.DO_NOT_ROLL_AGAIN, 0
            elif not doubles_rolled and current_player.state.number_of_turns_in_jail == 3:
                # It is the third turn in jail, so they must pay their way out...
                self.take_money_from_player(current_player, 50)
                current_player.state.is_in_jail = False
                current_player.state.number_of_turns_in_jail = 0
            else:
                # Doubles were rolled, so the player gets out of jail without paying,
                # but their turn will be over after this move even though doubles
                # were rolled...
                doubles_rolled = False  # We 'pretend' that doubles weren't rolled.
                current_player.state.is_in_jail = False
                current_player.state.number_of_turns_in_jail = 0

        # We check if doubles was rolled...
        roll_again = Game.Action.DO_NOT_ROLL_AGAIN
        if doubles_rolled:
            number_of_doubles_rolled += 1
            if number_of_doubles_rolled == 3:
                self.send_player_to_jail(current_player)
                return Game.Action.DO_NOT_ROLL_AGAIN, number_of_doubles_rolled
            else:
                roll_again = Game.Action.ROLL_AGAIN

        # We move the player to the new square...
        current_player.state.square += self.most_recent_total_dice_roll
        if current_player.state.square >= Board.NUMBER_OF_SQUARES:
            current_player.state.square -= Board.NUMBER_OF_SQUARES

            # If the player has passed Go, they get £200.
            # Note that we don't give £200 for landing on Go, as the
            # square itself does this...
            if current_player.state.square != 0:
                Logger.log("{0} gets £200 for passing Go".format(current_player.name))
                current_player.state.cash += 200

        # We perform any actions appropriate for the new square
        # the player has landed on...
        self.player_has_changed_square(current_player)

        # If the player has ended up in jail, their turn is over
        # (even if doubles were rolled)...
        if current_player.state.is_in_jail is True:
            roll_again = Game.Action.DO_NOT_ROLL_AGAIN

        return roll_again, number_of_doubles_rolled

    def player_has_changed_square(self, current_player):
        '''
        Called when the player has moved squares.

        We take whatever action is appropriate for the square landed on.
        '''
        square = self.state.board.squares[current_player.state.square]
        Logger.log("Moved to {0}".format(square.name))

        # We notify all players that the player has landed
        # on this square...
        for player in self.state.players:
            player.call_ai(player.ai.player_landed_on_square, self.state, square, current_player)

        # We perform the square's landed-on action...
        square.landed_on(self, current_player)

    def take_money_from_player(self, player, amount):
        '''
        Takes some money from the player.

        The player is given the option to make a deal or
        mortgage properties first.

        Returns the money taken. In the case that the player has
        gone bankrupt, this may not be the same as the amount requested.
        '''
        # We tell the player that we need money from them...
        player.call_ai(player.ai.money_will_be_taken, player, amount)

        # We allow the player to make deals (if this money-taking was
        # not itself the result of making a deal)...
        if not self._in_make_deals:
            self._make_deals(player)

        # We allow the player to sell houses...
        self._sell_houses(player)

        # We allow the player to mortgage properties...
        self._mortgage_properties(player)

        # We take the money, and tell the player that it was taken...
        cash_before_money_taken = player.state.cash
        player.state.cash -= amount
        player.call_ai(player.ai.money_taken, player, amount)

        # And log it...
        Logger.log("{0} pays £{1}".format(player.name, amount))

        # We return the amount taken...
        if player.state.cash >= 0:
            return amount
        else:
            return cash_before_money_taken

    def give_money_to_player(self, player, amount):
        '''
        Gives some money to the player.
        '''
        # We give the money to the player and tell them about it...
        player.state.cash += amount
        player.call_ai(player.ai.money_given, player, amount)

        # And log it...
        Logger.log("{0} gets £{1}".format(player.name, amount))

    def transfer_cash(self, from_player, to_player, amount, action):
        '''
        Transfers money between the two players.

        Actions (enums of type Game.Action):
        - ROLLBACK_ON_INSUFFICIENT_CASH
        - PAY_AS_MUCH_AS_POSSIBLE

        Returns (enums of type Game.Action):
        - TRANSFER_SUCCEEDED
        - TRANSFER_FAILED
        '''

        # We try taking the money from the player (they have a chance to make
        # deals or sell property when this happens)...
        amount_taken = self.take_money_from_player(from_player, amount)
        if from_player.state.cash >= 0:
            # They had enough money so we give it to the to_player...
            self.give_money_to_player(to_player, amount)
            return Game.Action.TRANSFER_SUCCEEDED

        # The player did not have enough money. What we do depends on the action
        # passed in...
        if action == Game.Action.PAY_AS_MUCH_AS_POSSIBLE:
            # We pay the to-player as much as possible. This still
            # leaves the from_player with a negative amount of cash
            # as if the whole amount had been taken...
            self.give_money_to_player(to_player, amount_taken)
        elif action == Game.Action.ROLLBACK_ON_INSUFFICIENT_CASH:
            # We roll back the transfer...
            self.give_money_to_player(from_player, amount)

        return Game.Action.TRANSFER_FAILED

    def send_player_to_jail(self, player):
        '''
        Sends the player to jail.
        '''
        player.state.is_in_jail = True
        player.state.number_of_turns_in_jail = 0
        player.state.square = self.state.board.get_index(Square.Name.JAIL)
        self.player_has_changed_square(player)

    def give_property_to_player(self, player, square_name):
        '''
        Gives a named property to a player.

        Returns the property square.
        '''
        Logger.log("{0} gets {1}".format(player.name, square_name))

        # The square on the board is given the player number of its owner,
        # and the player is given the index of the square on the board.
        # So they both know about each other...
        square = self.state.board.get_square_by_name(square_name)
        square.owner = player
        player.state.properties.add(square)

        # We update which sets are owned by which players, as this
        # may have changed...
        self._update_sets()

        return square

    def transfer_property(self, from_player, to_player, square_name):
        '''
        Transfers the named property from from_player to to_player.
        '''
        Logger.log("{0} transfered from {1} to {2}".format(
            square_name, from_player.name, to_player.name))

        # We get the Property object...
        square = self.state.board.get_square_by_name(square_name)

        # We update the owner and the collections managed by each player...
        square.owner = to_player
        to_player.state.properties.add(square)
        from_player.state.properties.remove(square)

        # We update which sets are owned by which players, as this
        # may have changed...
        self._update_sets()

    def offer_property_for_sale(self, current_player, square):
        '''
        Offers the property for sale, initially to the current player.
        If they do not want it, it is then offered for auction to all
        players.
        '''
        # We first offer the property to the current player...
        action = self._offer_property_to_current_player(current_player, square)
        if action == Game.Action.PROPERTY_BOUGHT:
            return

        # The current player did not buy the property, so we put it
        # up for auction...
        self._offer_property_for_auction(square)

    def _offer_property_for_auction(self, square):
        '''
        We request bids from each player and sell to the highest bidder.
        If the highest bidder cannot actually pay, it goes to the next
        highest (and so on).
        '''
        Logger.log("{0} offered for auction".format(square.name), Logger.INFO)
        Logger.indent()

        # We get bids from each player and store them in a list of
        # tuples of (player, bid)...
        bids = []
        for player_who_won_auction in self.state.players:
            # We get a bid from the player and make sure that
            # it's an integer amount...
            bid = player_who_won_auction.call_ai(
                player_who_won_auction.ai.property_offered_for_auction,
                self.state,
                player_who_won_auction,
                square)

            # A bid of zero (or below) is not a bid...
            if bid > 0:
                bids.append((player_who_won_auction, bid))

        # We sort the bids from high to low...
        bids.sort(key=lambda x: x[1], reverse=True)

        # We log the bids...
        readable_bids = [(player.name, bid) for (player, bid) in bids]
        Logger.log("Bids: {0}".format(readable_bids))

        status = PlayerAIBase.Action.AUCTION_FAILED
        player_who_won_auction = None
        selling_price = 0

        # We sell to the highest bidder...
        number_of_bids = len(bids)
        for i in range(number_of_bids):
            player_who_won_auction = bids[i][0]

            # We find the next highest bid...
            if i+1 < number_of_bids:
                next_highest_bid = bids[i+1][1]
            else:
                next_highest_bid = 0
            selling_price = next_highest_bid + 1

            # We sell it to the player...
            self.take_money_from_player(player_who_won_auction, selling_price)
            if player_who_won_auction.state.cash < 0:
                # The player did not have enough money, so we refund what we
                # took and sell the property to the next highest bidder...
                self.give_money_to_player(player_who_won_auction, selling_price)
            else:
                # The player successfully bought the property...
                self.give_property_to_player(player_who_won_auction, square.name)
                status = PlayerAIBase.Action.AUCTION_SUCCEEDED
                break

        # We notify all the players...
        for player in self.state.players:
            player.call_ai(player.ai.auction_result, status, square, player_who_won_auction, selling_price)

        Logger.dedent()

    def _offer_property_to_current_player(self, player, square):
        '''
        Offers the property to the current player.

        Returns Game.Action.PROPERTY_BOUGHT or PROPERTY_NOT_BOUGHT.
        '''
        # We ask the player if they want to buy the property...
        action = player.call_ai(player.ai.landed_on_unowned_property, self.state, player, square)
        if action == PlayerAIBase.Action.DO_NOT_BUY:
            return Game.Action.PROPERTY_NOT_BOUGHT

        # The player wants to buy the property, so we take the money...
        self.take_money_from_player(player, square.price)

        if player.state.cash < 0:
            # The player did not have enough money, so we revert the transaction...
            self.give_money_to_player(player, square.price)
            return Game.Action.PROPERTY_NOT_BOUGHT
        else:
            # The purchase was successful...
            self.give_property_to_player(player, square.name)
            return Game.Action.PROPERTY_BOUGHT

    def _update_sets(self):
        '''
        Called after any properties have been bought or otherwise
        changed hands, to keep the information about which players
        own which sets up to date.
        '''
        # We find which players own sets, and put this info
        # into the Player objects...
        all_sets = self.state.board.get_owned_sets(include_mortgaged_sets=True)
        unmortgaged_sets = self.state.board.get_owned_sets(include_mortgaged_sets=False)
        for player in self.state.players:
            player.state.owned_unmortgaged_sets = unmortgaged_sets[player]
            player.state.owned_sets = all_sets[player]

    def _build_houses(self, current_player):
        '''
        We give the current player the option to build houses.
        '''
        # We only offer the chance to build if the player owns
        # at least one complete, unmortgaged set...
        if not current_player.state.owned_unmortgaged_sets:
            return

        # We ask the player if he wants to build any houses.
        # build_instructions is a list of tuples like:
        # (street_name, number_of_houses)
        build_instructions = current_player.call_ai(current_player.ai.build_houses, self.state, current_player)
        if not build_instructions:
            return

        Logger.log("{0} wants to build houses: {1}".format(current_player.name, build_instructions))
        Logger.indent()

        # There are a number of ways that building can fail. Some are
        # hard to see without doing the transaction first. So we first do
        # the building and take the money then check that everything looks
        # OK. If not, we roll back...
        self._build_houses_and_take_money(current_player, build_instructions)

        # Did the player have enough money?
        if current_player.state.cash < 0:
            Logger.log("{0} does not have enough cash".format(current_player.name))
            self._roll_back_house_building(current_player, build_instructions)
            Logger.dedent()
            return

        # We check each street to see if it looks as we expect...
        for (street, number_of_houses) in build_instructions:
            # Did the player try to build a -ve number of houses?
            if number_of_houses < 0:
                Logger.log("Negative number of houses specified")
                self._roll_back_house_building(current_player, build_instructions)
                Logger.dedent()
                return

            # Does the street have more than five houses?
            if street.number_of_houses > 5:
                Logger.log("Too many houses requested")
                self._roll_back_house_building(current_player, build_instructions)
                Logger.dedent()
                return

            # Is the set that this street is a part of wholly owned by
            # the current player, and unmortgaged?
            if street.property_set not in current_player.state.owned_unmortgaged_sets:
                Logger.log("Set now fully owned, or partly mortgaged")
                self._roll_back_house_building(current_player, build_instructions)
                Logger.dedent()
                return

            # We check if the set that this street is part of has been
            # built in a balanced way...
            if not self._set_has_balanced_houses(street.property_set):
                Logger.log("Building was unbalanced")
                self._roll_back_house_building(current_player, build_instructions)
                Logger.dedent()
                return

        Logger.log("Houses built successfully")
        Logger.dedent()

    def _set_has_balanced_houses(self, property_set):
        '''
        Returns True if the set has balanced housing, False if not.
        '''
        houses_for_each_property = [p.number_of_houses for p in property_set.properties]
        if max(houses_for_each_property) - min(houses_for_each_property) <= 1:
            return True
        else:
            return False

    def _build_houses_and_take_money(self, current_player, build_instructions):
        '''
        Builds the houses passed in and takes the money from the player.

        build_instructions is a list of tuples like:
        (square_name, number_of_houses, Street-object)
        '''
        # We build the houses...
        total_cost = 0
        for (street, number_of_houses) in build_instructions:
            street.number_of_houses += number_of_houses
            total_cost += (street.house_price * number_of_houses)

        # And take the money...
        self.take_money_from_player(current_player, total_cost)

    def _roll_back_house_building(self, current_player, build_instructions):
        '''
        Removes the houses specified and refunds the money.
        '''
        # We remove the houses...
        total_cost = 0
        for (street, number_of_houses) in build_instructions:
            street.number_of_houses -= number_of_houses
            total_cost += (street.house_price * number_of_houses)

        # And refund the money...
        self.give_money_to_player(current_player, total_cost)

    def _mortgage_properties(self, current_player):
        '''
        We give the current player the option to mortgage properties.
        '''
        # We ask the player if they want to mortgage anything...
        properties_to_mortgage = current_player.call_ai(
            current_player.ai.mortgage_properties,
            self.state,
            current_player)
        if not properties_to_mortgage:
            return

        # We mortgage them...
        total_mortgage_value = 0
        for square in properties_to_mortgage:
            # We check that the square is a property...
            if not isinstance(square, Property):
                continue

            # We check that the current player owns the property and
            # that they are not sneakily trying to mortgage someone
            # else's property...
            if square.owner is not current_player:
                continue

            # We check that the property is not already mortgaged...
            if square.is_mortgaged is True:
                continue

            # We check that there are no houses on the property.
            # (You can't mortgage if a property has houses.)
            if isinstance(square, Street):
                if square.number_of_houses != 0:
                    continue

            # We mortgage the property...
            square.is_mortgaged = True
            total_mortgage_value += square.mortgage_value

        # We give the money to the player and update the owned
        # sets, as they may have changed...
        self.give_money_to_player(current_player, total_mortgage_value)
        self._update_sets()

    def _sell_houses(self, current_player):
        '''
        We offer the player the chance to sell houses.
        '''
        # We ask the player which properties they want to sell...
        sale_instructions = current_player.call_ai(
            current_player.ai.sell_houses,
            self.state,
            current_player)
        if not sale_instructions:
            return

        # We first remove the houses from the board, then check that things
        # look good. We may have to replace them if things don't look OK.
        sale_value = self._remove_houses(sale_instructions)

        # A few checks...
        for (street, number_of_houses) in sale_instructions:

            # We check that the player isn't trying to sell a negative
            # number of houses. (As a sneaky way of buying houses cheaply.)
            if number_of_houses < 0:
                self._replace_houses(sale_instructions)
                return

            # We check that the property has been left with between 0 and 5 houses...
            if street.number_of_houses < 0 or street.number_of_houses > 5:
                self._replace_houses(sale_instructions)
                return

            # We check that the street belongs to the current player...
            if street.owner is not current_player:
                self._replace_houses(sale_instructions)
                return

            # Will the sale result in unbalanced housing?
            if not self._set_has_balanced_houses(street.property_set):
                self._replace_houses(sale_instructions)
                return

        # The sale looks good, so we give the player the money...
        self.give_money_to_player(current_player, sale_value)

    def _remove_houses(self, instructions):
        '''
        Removes houses from the board when they are being sold.

        Returns the total sale value.
        '''
        total_sale_value = 0
        for (street, number_of_houses) in instructions:
            street.number_of_houses -= number_of_houses
            sale_price = int(street.house_price / 2)
            total_sale_value += (number_of_houses * sale_price)

        return total_sale_value

    def _replace_houses(self, instructions):
        '''
        Replaces houses on the board if a sale of them was unsuccessful.
        '''
        for (street, number_of_houses) in instructions:
            street.number_of_houses += number_of_houses

    def _get_out_of_jail(self, current_player):
        '''
        If the player is in jail, they get a chance to buy their way out
        or to play a Get Out Of Jail Free card.
        '''
        if not current_player.state.is_in_jail:
            return

        # We ask the player if they want to buy their way out or play a card...
        action = current_player.call_ai(
            current_player.ai.get_out_of_jail,
            self.state,
            current_player)
        if action == PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL:
            # The player is buying their way out...
            self.take_money_from_player(current_player, 50)
            current_player.state.is_in_jail = False
            current_player.state.number_of_turns_in_jail = 0

        elif action == PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD:
            # The player is playing a Get Out Of Jail Free card...
            if current_player.state.number_of_get_out_of_jail_free_cards >= 1:

                # We put it back in its deck...
                card = current_player.state.get_out_of_jail_free_cards[0]
                card.put_back_in_deck()

                # And take it fro the player...
                del current_player.state.get_out_of_jail_free_cards[0]

                # We remove the player from jail...
                current_player.state.is_in_jail = False
                current_player.state.number_of_turns_in_jail = 0

    def _unmortgage_properties(self, current_player):
        '''
        We give the player the opportunity to unmortgage properties.
        '''

        # We ask the player if they want to unmortgage anything...
        squares = current_player.call_ai(
            current_player.ai.unmortgage_properties,
            self.state,
            current_player)
        if not squares:
            return

        # We calculate the cost to unmortgage these properties. This is
        # 55% of their total face value...
        unmortgage_cost = 0
        for square in squares:
            # Is the square a property?
            if not isinstance(square, Property):
                continue

            # We check if the property is owned by the current player...
            if square.owner is not current_player:
                return

            unmortgage_cost += int(square.mortgage_value * 1.1)

        # We take the money from the player...
        self.take_money_from_player(current_player, unmortgage_cost)

        if current_player.state.cash < 0:
            # The player did not have enough money, so we refund it and abort the
            # transaction...
            self.give_money_to_player(current_player, unmortgage_cost)
        else:
            # The player successfully paid, so we unmortgage the properties...
            for square in squares:
                square.is_mortgaged = False

        # We update the info about which sets are mortgaged and unmortgaged...
        self._update_sets()

    def _make_deals(self, current_player):
        '''
        The player can make up to three deals.
        '''
        self._in_make_deals = True
        for i in range(3):
            self._make_deal(current_player)
        self._in_make_deals = False

    def _make_deal(self, current_player):
        '''
        Lets the player propose a deal.
        '''
        # We see if the player wants to propose a deal...
        proposal = current_player.call_ai(
            current_player.ai.propose_deal,
            self.state,
            current_player)
        if not proposal:
            return

        # We find the player the deal is being proposed to (checking that the
        # player is valid first)...
        if proposal.propose_to_player is None:
            current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED)
            return
        proposed_to_player = proposal.propose_to_player

        Logger.log("{0} proposed deal to {1}: {2}".format(current_player.name, proposed_to_player.name, proposal))
        Logger.indent()

        # We check that the players own the properties specified. If any of the
        # properties have houses, then the whole set must be part of the deal...
        board = self.state.board

        # A nested function to validate property ownership...
        def validate_properties(player, properties):
            for property in properties:
                # Does the player own the property?
                if player.owns_properties([property]) is False:
                    return False

                # The player owns the property, but if it has houses we need
                # to check that the whole set is part of the deal...
                if isinstance(property, Street) and property.number_of_houses > 0:
                    properties_in_set = property.property_set.properties
                    all_properties_part_of_deal = set(properties).issuperset(set(properties_in_set))
                    if all_properties_part_of_deal is False:
                        return False
            return True

        if validate_properties(current_player, proposal.properties_offered) is False:
            current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED)
            Logger.dedent()
            return
        if validate_properties(proposed_to_player, proposal.properties_wanted) is False:
            current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED)
            Logger.dedent()
            return

        # We pass the proposal to the proposee, after redacting the cash offer info
        # and setting the player who proposed the deal...
        maximum_cash_offered = proposal.maximum_cash_offered
        minimum_cash_wanted = proposal.minimum_cash_wanted
        proposal.maximum_cash_offered = 0
        proposal.minimum_cash_wanted = 0
        proposal.proposed_by_player = current_player

        response = proposed_to_player.call_ai(
            proposed_to_player.ai.deal_proposed,
            self.state,
            proposed_to_player,
            proposal)

        if response.action == DealResponse.Action.REJECT:
            # The proposee rejected the deal...
            current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.DEAL_REJECTED)
            proposed_to_player.call_ai(proposed_to_player.ai.deal_result, PlayerAIBase.DealInfo.DEAL_REJECTED)
            Logger.log("{0} rejected the deal".format(proposed_to_player.name))
            Logger.dedent()
            return

        # The deal has been accepted, but is it actually acceptable in
        # terms of cash exchange to both parties?
        cash_transfer_from_proposer_to_proposee = 0
        if minimum_cash_wanted > 0:
            # The proposer wants money. Did the proposee offer enough?
            if response.maximum_cash_offered < minimum_cash_wanted:
                current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.ASKED_FOR_TOO_MUCH_MONEY)
                proposed_to_player.call_ai(proposed_to_player.ai.deal_result, PlayerAIBase.DealInfo.OFFERED_TOO_LITTLE_MONEY)
                Logger.log("Deal rejected: {0} asked for more than {1} was willing to pay".format(
                    current_player.name, proposed_to_player.name))
                Logger.dedent()
                return
            cash_transfer_from_proposer_to_proposee = -1 * (minimum_cash_wanted + response.maximum_cash_offered) / 2

        elif maximum_cash_offered > 0:
            # The proposer offered money. Was this enough for the proposee?
            if maximum_cash_offered < response.minimum_cash_wanted:
                current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.OFFERED_TOO_LITTLE_MONEY)
                proposed_to_player.call_ai(proposed_to_player.ai.deal_result, PlayerAIBase.DealInfo.ASKED_FOR_TOO_MUCH_MONEY)
                Logger.log("Deal rejected: {0} offered less than {1} was willing to accept".format(
                    current_player.name, proposed_to_player.name))
                Logger.dedent()
                return
            cash_transfer_from_proposer_to_proposee = (maximum_cash_offered + response.minimum_cash_wanted) / 2

        # The deal is acceptable to both parties, so we transfer the money...
        cash_transfer_from_proposer_to_proposee = int(cash_transfer_from_proposer_to_proposee)
        if cash_transfer_from_proposer_to_proposee > 0:
            # We transfer cash from the proposer to the proposee...
            result = self.transfer_cash(
                current_player,
                proposed_to_player,
                cash_transfer_from_proposer_to_proposee,
                Game.Action.ROLLBACK_ON_INSUFFICIENT_CASH)
        elif cash_transfer_from_proposer_to_proposee < 0:
            # We transfer cash from the proposee to the proposer...
            result = self.transfer_cash(
                proposed_to_player,
                current_player,
                cash_transfer_from_proposer_to_proposee * -1,
                Game.Action.ROLLBACK_ON_INSUFFICIENT_CASH)
        else:
            # No money is changing hands, so the case (non) transfer 'succeeds'...
            result = Game.Action.TRANSFER_SUCCEEDED

        if result == Game.Action.TRANSFER_FAILED:
            current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY)
            proposed_to_player.call_ai(proposed_to_player.ai.deal_result, PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY)
            Logger.log("Deal accepted, but player did not have enough money")
            Logger.dedent()
            return

        # The cash transfer worked, so we transfer the properties...
        Logger.log("Deal successful")
        for property in proposal.properties_offered:
            self.transfer_property(current_player, proposed_to_player, property.name)

        for property in proposal.properties_wanted:
            self.transfer_property(proposed_to_player, current_player, property.name)

        # We tell the players that the deal succeeded...
        current_player.call_ai(current_player.ai.deal_result, PlayerAIBase.DealInfo.SUCCEEDED)
        proposed_to_player.call_ai(proposed_to_player.ai.deal_result, PlayerAIBase.DealInfo.SUCCEEDED)

        # We let all players know the details of the deal that just took place...
        deal_result = DealResult()
        deal_result.proposer = current_player
        deal_result.proposee = proposed_to_player
        deal_result.properties_transferred_to_proposer = proposal.properties_wanted
        deal_result.properties_transferred_to_proposee = proposal.properties_offered
        deal_result.cash_transferred_from_proposer_to_proposee = cash_transfer_from_proposer_to_proposee
        for player in self.state.players:
            player.call_ai(player.ai.deal_completed, deal_result)

        Logger.dedent()

    def _check_game_status(self):
        '''
        Checks if the game has a winner.
        '''
        # We see how many players still have money...
        solvent_players = {player for player in self.state.players if player.state.cash >= 0}
        number_of_solvent_players = len(solvent_players)
        if number_of_solvent_players > 1:
            self.status = Game.Action.GAME_NOT_OVER
        elif number_of_solvent_players == 1:
            self.status = Game.Action.GAME_OVER
            self.winner = solvent_players.pop()
        else:
            self.status = Game.Action.GAME_OVER

    def _check_for_bankrupt_players(self):
        '''
        Checks if any players have gone bankrupt.
        Any player can go bankrupt in any turn, even not their own,
        for example as the result of a "Collect X from player" card.
        '''
        # We check each player to see if they are bankrupt.
        # Note that we iterate through a copy of the collection of players, as
        # we may remove players from the list...
        list_players = list(self.state.players)
        for player in list_players:
            if player.state.cash < 0:
                self._player_went_bankrupt(player)

    def _player_went_bankrupt(self, current_player):
        '''
        Called when a player has gone bankrupt.
        '''
        Logger.log("{0} went bankrupt".format(current_player.name))

        # We notify all players that this player went bankrupt...
        for player in self.state.players:
            player.call_ai(player.ai.player_went_bankrupt, current_player)

        # We remove the player from the game...
        self._remove_player(current_player)

    def _player_ran_out_of_time(self, current_player):
        '''
        Called when a player has run out of time.
        '''
        Logger.log("{0} ran out of time".format(current_player.name))

        # We notify all players that this player went bankrupt...
        for player in self.state.players:
            player.call_ai(player.ai.player_ran_out_of_time, current_player)

        # We remove the player from the game...
        self._remove_player(current_player)

    def _remove_player(self, player):
        '''
        Removes the player from the game and returns all properties to the bank.
        '''
        # We return properties to the bank...
        board = self.state.board
        for property in player.state.properties:
            property.owner = None
            property.number_of_houses = 0
            property.is_mortgaged = False
        player.state.properties.clear()

        # We update who owns which sets...
        self._update_sets()

        # We return any Get Out Of Jail Free cards to their decks...
        for card in player.state.get_out_of_jail_free_cards:
            card.put_back_in_deck()

        # We move the player to the bankrupt list...
        player.state.cash = -1
        player.state.square = -1
        self.state.players.remove(player)
        self.state.bankrupt_players.append(player)

    def _find_winner(self):
        '''
        The winner is the player with the highest net worth.
        If the game is over because only one player remains, then they
        automatically have the highest net worth. If the game went to the
        maximum number of rounds, we choose between the remaining players.
        '''
        # We find the maximum net worth and the collection of players
        # with this net worth...
        if len(self.state.players) == 0:
            self.winner = None
            return

        max_net_worth = max(player.net_worth for player in self.state.players)
        winning_players = [player for player in self.state.players if player.net_worth == max_net_worth]

        # If there is only one player, then they have won...
        if(len(winning_players) == 1):
            self.winner = winning_players[0]
            Logger.log("Game over. Winner is: {0}".format(self.winner.ai.get_name()))
        else:
            self.winner = None
            Logger.log("Game over. Draw.")

        # We notify all the players...
        maximum_rounds_played = (self.number_of_rounds_played == self.maximum_rounds)
        for player in self.state.players:
            player.ai.game_over(self.winner, maximum_rounds_played)
        for player in self.state.bankrupt_players:
            player.ai.game_over(self.winner, maximum_rounds_played)

    def _check_eminent_domain_rule(self):
        '''
        Checks if we should play the eminent domain rule, and plays it
        if we should.

        At a certain turn (say turn 200), if no player has built houses,
        then we compulsorily purchase all properties and re-auction them.
        '''

        # We check if the rule is set up...
        if self.eminent_domain is False:
            return

        # Is it the right turn to play the rule?
        if self.number_of_rounds_played != self.eminent_domain_round:
            return

        # The rule is enabled and it's the right round. Are all properties
        # without houses?
        properties_have_houses = False
        for square in self.state.board.squares:
            if isinstance(square, Street) and (square.number_of_houses != 0):
                properties_have_houses = True
                break

        # If any properties have houses, we don't apply the rule...
        if properties_have_houses is True:
            return

        # We want to play the rule!

        # First we buy back all the properties...
        for square in self.state.board.squares:

            # Is this square a property?
            if not isinstance(square, Property):
                continue

            # We've got a property, so we find the player and the price...
            owner = square.owner
            if owner is None:
                continue
            price = square.price if square.is_mortgaged is False else int(square.price/2)

            # We give the player the money and take the property...
            self.give_money_to_player(owner, price)
            square.owner = None
            square.is_mortgaged = False
            owner.state.properties.remove(square)

        # We update which sets each player owns...
        self._update_sets()

        # Now we auction all properties...
        for square in self.state.board.squares:

            # Is this square a property?
            if isinstance(square, Property):
                self._offer_property_for_auction(square)
