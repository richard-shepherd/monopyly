from .square import Square


# This is called GoToJailSquare to make the distinction clear between
# it and the GoToJailCard...
class GoToJailSquare(Square):
    '''
    Represents the Go To Jail square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.GO_TO_JAIL)

    def landed_on(self, game, player):
        '''
        Sends the player to jail.
        '''
        game.send_player_to_jail(player)

