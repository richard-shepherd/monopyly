from monopyly import *
from testing_utils import *

# TODO: max rounds, net worth (not just cash)

def test_maximum_rounds():
    '''
    Tests that the game is over when the maximum number of rounds
    has been played.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())

    # We put both players on Free Parking and ensure that all dice
    # are zeros. Player1 has more money, so after the maximum number
    # of rounds, they should win...
    player0.state.square = 20
    player1.state.square = 20
    player0.state.cash = 1000
    player0.state.cash = 1200

    # We play the game...
    game.dice = MockDice(roll_results=[(0, 0)], repeat=True)
    game.maximum_rounds = 20
    game.play_game()

    # We check the winner and the turns played...
    assert game.number_of_rounds_played == game.maximum_rounds
    assert game.winner == player1




