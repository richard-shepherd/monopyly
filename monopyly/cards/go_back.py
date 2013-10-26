from .card import Card


class GoBack(Card):
    '''
    Moves the player back to the square specified, ie without
    passing Go.
    '''

    def __init__(self, destination_square_name):
        '''
        The 'constructor'.
        '''
        self.destination_square_name = destination_square_name

    def play(self, game, current_player):
        '''
        Moves the player to the destination square.
        '''
        destination_square_index = game.state.board.get_index(self.destination_square_name)
        current_player.state.square = destination_square_index
        game.player_has_changed_square(current_player)

