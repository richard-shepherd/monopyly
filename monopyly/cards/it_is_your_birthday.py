from .card import Card


class ItIsYourBirthday(Card):
    '''
    It is your birthday. Collect £10 from each player.
    '''
    def play(self, game, current_player):
        '''
        The player gets £10 from each other player. ( £100 if the player
        does not say "Happy Birthday!")
        '''

        # We get £10 from each player...
        for player in game.state.players:
            if(player is current_player):
                continue

            # We see if the player says "Happy Birthday!"...
            message = player.ai.players_birthday()
            if(message == "Happy Birthday!"):
                amount = 10
            else:
                amount = 100

            # We take the money from the player, and give it to
            # the current player...
            game.take_money_from_player(player, amount)
            game.give_money_to_player(current_player, amount)

