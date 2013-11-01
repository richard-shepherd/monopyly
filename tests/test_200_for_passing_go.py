from monopyly import *
from testing_utils import *


def test_200_for_passing_go():
    '''
    Tests that you get £200 for passing Go.
    '''
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    # The player starts on Mayfair and rolls an 11 to get
    # to Just Visiting, passing Go in the process...
    player.state.square = 39
    game.dice = MockDice([(5, 6)])
    game.play_one_turn(player)

    # The player should be on Just Visiting, and have
    # an extra £200...
    assert player.state.square == 10
    assert player.state.cash == 1700




