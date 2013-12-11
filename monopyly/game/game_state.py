from .board import Board
from .player import Player
import copy


class GameState(object):
    '''
    Holds the state of the game.

    This is kept separate from the game mechanics (the Game class)
    to make it simpler to pass game state to AIs.
    '''

    def __init__(self):
        '''
        The 'constructor'.
        '''

        # The board...
        self.board = Board()

        # The collection of players (Player objects) playing the game...
        self.players = []

        # The collection of players who have gone bankrupt...
        self.bankrupt_players = []

    @property
    def number_of_players(self):
        '''
        The number of players.
        '''
        return len(self.players)

