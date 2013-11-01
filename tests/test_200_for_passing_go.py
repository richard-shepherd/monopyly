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


def test_landing_on_go():
    '''
    If you land on Go, you should get £200.
    '''
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    # The player starts on Park Lane and rolls a 3 to get
    # to Go...
    player.state.square = 37
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should be on Go, and have an extra £200...
    assert player.state.square == 0
    assert player.state.cash == 1700




