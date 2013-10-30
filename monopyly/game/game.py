from .dice import Dice
from .player import Player
from .game_state import GameState
from ..squares import Square


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
        ROLL_AGAIN = 1
        DO_NOT_ROLL_AGAIN = 2

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.state = GameState()
        self.dice = Dice()

    def add_player(self, ai):
        '''
        Adds a player AI.

        Returns the Player object created.
        '''
        # We wrap the AI up into a Player object...
        player_number = len(self.state.players)
        player = Player(ai, player_number)
        self.state.players.append(player)
        return player

    def play_game(self):
        '''
        Plays a game of monopoly.
        '''
        # We tell the players that the game is starting, and which
        # player-number they are...
        for player in self.state.players:
            player.ai.start_of_game(player.number)

        # TODO: Play the game!

    def play_one_round(self):
        '''
        Plays one round of the game, ie one turn for each of
        the players.

        The round can come to an end before all players' turns
        are finished if one of the players wins.
        '''
        for player in self.state.players:
            self.play_one_turn(player)

    def play_one_turn(self, current_player):
        '''
        Plays one turn for one player.
        '''
        # We notify all players that this player's turn is starting...
        for player in self.state.players:
            player.ai.start_of_turn(self.state.copy(), current_player.state.player_number)

        # TODO: Before the start of the turn we give the player an
        # option to perform deals or mortgage properties so that they
        # can raise money for house-building...

        # TODO: The player can build houses...

        # TODO: If the player is in jail, they can buy themselves out,
        # or play Get Out Of Jail Free.

        # This while loop manages rolling again if the player
        # rolls doubles...
        roll_again = Game.Action.ROLL_AGAIN
        number_of_doubles_rolled = 0
        while roll_again == Game.Action.ROLL_AGAIN:
            roll_again, number_of_doubles_rolled = self.roll_and_move(current_player, number_of_doubles_rolled)

    def roll_and_move(self, current_player, number_of_doubles_rolled):
        '''
        Rolls the dice, moves the player and takes the appropriate
        action for the square landed on.

        Returns whether we should roll again and the number of doubles rolled.
        '''
        # We roll the dice and move the player...
        roll1, roll2 = self.dice.roll()

        # We check if doubles was rolled...
        roll_again = Game.Action.DO_NOT_ROLL_AGAIN
        if(roll1 == roll2):
            # Doubles was rolled...
            number_of_doubles_rolled += 1
            if(number_of_doubles_rolled == 3):
                self.send_player_to_jail(current_player)
                return Game.Action.DO_NOT_ROLL_AGAIN, number_of_doubles_rolled
            else:
                roll_again = Game.Action.ROLL_AGAIN

        # We move the player to the new square...
        # TODO: Get £200 for passing Go.
        # TODO: Player doesn't move if in Jail.
        total_roll = roll1 + roll2
        self.state.board.move_player(current_player, total_roll)
        self.player_has_changed_square(current_player)

        # If the player has ended up in jail, their turn is over
        # (even if doubles were rolled)...
        if(current_player.state.in_jail is True):
            roll_again = Game.Action.DO_NOT_ROLL_AGAIN

        return roll_again, number_of_doubles_rolled

    def player_has_changed_square(self, current_player):
        '''
        Called when the player has moved squares.

        We take whatever action is appropriate for the square landed on.
        '''
        square = self.state.board.squares[current_player.state.square]

        # We notify all players that the player has landed
        # on this square...
        for player in self.state.players:
            player.ai.player_landed_on_square(self.state.copy(), square.name, player.state.player_number)

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
        player.ai.money_will_be_taken(player.state.copy(), amount)

        # TODO: We allow the player to make deals...

        # TODO: We allow the player to mortgage properties...

        # We take the money, and tell the player that it was taken...
        cash_before_money_taken = player.state.cash
        player.state.cash -= amount
        player.ai.money_taken(player.state.copy(), amount)

        # We return the amount taken...
        if(player.state.cash >= 0):
            return amount
        else:
            return cash_before_money_taken

    def give_money_to_player(self, player, amount):
        '''
        Gives some money to the player.
        '''
        # We give the money to the player and tell them about it...
        player.state.cash += amount
        player.ai.money_given(player.state.copy(), amount)

    def send_player_to_jail(self, player):
        '''
        Sends the player to jail.
        '''
        player.state.in_jail = True
        player.state.number_of_turns_in_jail = 0
        player.state.square = self.state.board.get_index(Square.Name.JAIL)
        self.player_has_changed_square(player)

    def give_property_to_player(self, player, square_name):
        '''
        Gives a named property to a player.
        '''
        # The square on the board is given the player number of its owner,
        # and the player is given the index of the square on the board.
        # So they both know about each other...
        index = self.state.board.get_index(square_name)
        square = self.state.board.get_square_by_index(index)
        square.owner_player_number = player.state.player_number
        player.state.property_indexes.add(index)

    def _update_sets(self):
        '''
        Called after any properties have been bought or otherwise
        changed hands, to keep the information about which players
        own which sets up to date.
        '''
        # We clear out the existing info...
        for player in self.state.players:
            player.state.sets_owned.clear()

        # We go through the sets, checking if one player owns
        # all the properties in them...
        # TODO: finish this



