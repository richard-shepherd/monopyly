from .square import Square


class Chance(Square):
    '''
    Represents one of the Chance squares.
    '''
    def __init__(self):
        '''
        The 'constructor'.
        '''
        super().__init__(Square.Name.CHANCE)

    def landed_on(self, game, player):
        '''
        Called when a player has landed on Chance.
        '''
        game.state.board.chance_deck.take_card(game, player)
