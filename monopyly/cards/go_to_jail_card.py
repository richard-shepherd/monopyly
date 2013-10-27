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
        game.send_player_to_jail(current_player)

