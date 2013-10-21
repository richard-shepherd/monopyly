from .dice import Dice
from .player import Player
from .game_state import GameState


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

    def __init__(self):
        '''
        The 'constructor'.
        '''
        self.game_state = GameState()
        self.dice = Dice()

    def add_player(self, ai):
        '''
        Adds a player AI.
        '''
        # We wrap the AI up into a Player object...
        player_number = len(self.game_state.players) + 1
        self.game_state.players.append(Player(ai, player_number))

    def play_game(self):
        '''
        Plays a game of monopoly.
        '''
        # We tell the players that the game is starting, and which
        # player-number they are...
        for player in self.game_state.players:
            player.ai.start_of_game(player.number)

    def play_one_round(self):
        '''
        Plays one round of the game, ie one turn for each of
        the players.

        The round can come to an end before all players' turns
        are finished if one of the players wins.
        '''
        for player in self.game_state.players:
            self.play_one_turn(player)

    def play_one_turn(self, current_player):
        '''
        Plays one turn for one player.
        '''
        # We notify all players that this player's turn is starting...
        for player in self.game_state.players:
            game_state = self.game_state.copy()
            player.ai.start_of_turn(game_state, current_player.number)

