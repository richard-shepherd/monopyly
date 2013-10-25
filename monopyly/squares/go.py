from .square import Square


class Go(Square):
    '''
    Represents the Go square.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.GO)

    def landed_on(self, game, player):
        '''
        When a player lands on Go they get £200.
        '''
        game.give_money_to_player(player, 200)

