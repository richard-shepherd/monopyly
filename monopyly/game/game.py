from .board import Board
from .dice import Dice
from .player import Player


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
        self.board = Board()
        self.dice = Dice()
        self.players = []

    def add_player(self, player_ai):
        '''
        Adds a player AI.
        '''
        # We wrap the AI up into a Player object...
        self.players.append(Player(player_ai))


