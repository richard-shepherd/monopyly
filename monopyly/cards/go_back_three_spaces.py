from .card import Card
from ..game import Board


class GoBackThreeSpaces(Card):
    '''
    Go back three spaces.
    '''
    def play(self, game, current_player):

        # We move the player back three squares...
        current_player.state.square -= 3
        if(current_player.state.square < 0):
            current_player.state.square += Board.NUMBER_OF_SQUARES

        game.player_has_changed_square(current_player)



