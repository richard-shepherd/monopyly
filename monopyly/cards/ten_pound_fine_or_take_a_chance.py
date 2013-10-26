from .card import Card


class TenPoundFineOrTakeAChance(Card):
    '''
    Pay a £10 fine or take a Chance.
    '''

    class Action(object):
        '''
        A 'enum' for the actions.
        '''
        PAY_TEN_POUND_FINE = 0
        TAKE_A_CHANCE = 1

    def play(self, game, current_player):
        '''
        We ask the player whether they want to pay the fine
        or take a Chance.
        '''
        action = current_player.ai.pay_ten_pounds_or_take_a_chance()
        if(action == TenPoundFineOrTakeAChance.Action.PAY_TEN_POUND_FINE):
            game.take_money_from_player(current_player, 10)
        else:
            game.state.board.chance_deck.take_card(game, current_player)



