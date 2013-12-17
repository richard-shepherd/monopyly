from .card import Card


class TenPoundFineOrTakeAChance(Card):
    '''
    Pay a £10 fine or take a Chance.
    '''

    def play(self, game, current_player):
        '''
        We ask the player whether they want to pay the fine
        or take a Chance.
        '''
        # A delayed import to avoid circular importing...
        from ..game import PlayerAIBase

        action = current_player.ai.pay_ten_pounds_or_take_a_chance(game.state, current_player)
        if action == PlayerAIBase.Action.PAY_TEN_POUND_FINE:
            game.take_money_from_player(current_player, 10)
        else:
            game.state.board.chance_deck.take_card(game, current_player)



