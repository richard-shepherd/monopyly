from .square import Square


class Jail(Square):
    '''
    Represents the Jail / Just Visiting square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.JAIL)

    def landed_on(self, game, player):
        '''
        Nothing happens when you land on this square.

        If you were sent to jail, then the thing that caused this
        will have set the player as being in jail.
        '''
        pass
