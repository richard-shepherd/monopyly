
class DividendOfFifty(object):
    '''
    Bank pays you a dividend of £50.
    '''
    def played(self, game, player):
        game.give_money_to_player(player, 50)

