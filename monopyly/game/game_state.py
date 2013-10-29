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

    def copy(self):
        '''
        Returns a copy of the game state.
        '''
        # We create a deep copy of the game...
        game_copy = copy.deepcopy(self)

        # Then we 'redact' some information...
        for player in game_copy.players:
            player._ai = None

    @property
    def number_of_players(self):
        '''
        The number of players.
        '''
        return len(self.players)
