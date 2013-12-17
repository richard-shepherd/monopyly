from monopyly import *
from testing_utils import *


def test_ten_pound_fine_or_take_a_chance():
    '''
    Tests the "Take a £10 fine or take a Chance" card.
    '''

    # A player who pays the fine...
    class PlayerWhoPaysFine(DefaultPlayerAI):
        def pay_ten_pounds_or_take_a_chance(self, game_state, player):
            return PlayerAIBase.Action.PAY_TEN_POUND_FINE

    # A player who takes a Chance...
    class PlayerWhoTakesAChance(DefaultPlayerAI):
        def pay_ten_pounds_or_take_a_chance(self, game_state, player):
            return PlayerAIBase.Action.TAKE_A_CHANCE

    # We set up a game with the two players...
    game = Game()
    player_who_pays_fine = game.add_player(PlayerWhoPaysFine())
    player_who_takes_a_chance = game.add_player(PlayerWhoTakesAChance())

    # We mock the Chance deck...
    game.state.board.chance_deck = MockCardDeck(RewardCard(120))

    # We play the card on the player who pays the fine...
    card = TenPoundFineOrTakeAChance()
    card.play(game, player_who_pays_fine)
    assert player_who_pays_fine.state.cash == 1490

    # We play the card on the player who takes a chance...
    card.play(game, player_who_takes_a_chance)
    assert player_who_takes_a_chance.state.cash == 1620





