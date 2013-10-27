from .card import Card
from ..squares import Square


# Note: This class is called GoToJailCard make the distinction clear
# between it and the GoToJailSquare...
class GoToJailCard(Card):
    '''
    Go to Jail. Go directly to jail. Do not pass Go. Do not collect £200.
    '''
    def play(self, game, current_player):
        '''
        Moves the player to Jail.
        '''
        current_player.state.in_jail = True
        current_player.state.number_of_turns_in_jail = 0
        current_player.state.square = game.state.board.get_index(Square.Name.JAIL)
        game.player_has_changed_square(current_player)

