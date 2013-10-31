from monopyly import *
from testing_utils import *


def test_all_squares_implemented():
    '''
    Tests that all squares have their landed_on method implemented.
    '''
    # To test this, we start at Go and move round the board
    # one square at a time...
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    player.state.square = 0
    mock_dice = MockDice()
    game.dice = mock_dice

    for i in range(40):
        mock_dice.set_roll_results([(0,1)])
        game.play_one_turn(player)

    # There are no assertions in this test.
    # We are just checking that we don't get any
    # not-implemented exceptions from any of the squares.