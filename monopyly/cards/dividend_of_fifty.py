from .card import Card


class DividendOfFifty(Card):
    '''
    Bank pays you a dividend of £50.
    '''
    def played(self, game, current_player):
        game.give_money_to_player(current_player, 50)

