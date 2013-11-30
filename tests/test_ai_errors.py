from monopyly import *
from testing_utils import *

# TODO: build houses
# TODO: sell houses
# TODO: build houses invalid property names "VIME STREET"
# TODO: sell houses invalid property names "VIME STREET"
# TODO: mortgage properties invalid property names "VIME STREET"
# TODO: unmortgage properties invalid property names "VIME STREET"
# TODO: get out of jail
# TODO: propose deal
# TODO: deal proposed

class AIErrorRecorder(PlayerAIBase):
    '''
    Player who records the ai error messages.
    '''
    def __init__(self):
        self.message = ""

    def ai_error(self, message):
        self.message = message


def test_player_buys_property():
    '''
    The player returns the wrong type from the landed_on_unowned_property method.
    '''
    class TestPlayer(AIErrorRecorder):
        def landed_on_unowned_property(self, game_state, player_state, property_name, price):
            return "BUY"

    game = Game()
    player = game.add_player(TestPlayer())
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)
    assert "Invalid return type" in player.ai.message


def test_player_bids_in_auction():
    '''
    The player returns the wrong type from the property_offered_for_auction method.
    '''
    class TestPlayer(AIErrorRecorder):
        def property_offered_for_auction(self, game_state, player_state, property_name, face_value):
            return "45.6"

    game = Game()
    player = game.add_player(TestPlayer())
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)
    assert "Invalid return type" in player.ai.message

