from .card import Card


class ElectedChairman(Card):
    '''
    You have been elected chairman of the board.
    Pay each player £50.
    '''
    def play(self, game, current_player):
        # We take the money from the player...
        amount_to_pay = (game.state.number_of_players - 1) * 50
        game.take_money_from_player(current_player, amount_to_pay)
        if current_player.state.cash < 0:
            return

        # And give 50 to each player (if the current-player had enough cash)...
        for player in game.state.players:
            if player is not current_player:
                game.give_money_to_player(player, 50)



