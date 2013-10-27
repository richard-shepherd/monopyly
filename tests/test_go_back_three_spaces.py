from monopyly import *
from testing_utils import *


def test_go_back_three_spaces():
    '''
    Tests the "Go back three spaces" card.
    '''
    # We set up a game...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # We put the player on square 7 (Chance) and
    # play the card...
    player.state.square = 7
    card = GoBackThreeSpaces()
    card.play(game, player)

    # The player should be on Income Tax (and have £200 less)...
    assert player.state.square == 4
    assert player.state.cash == 1300

    # We put the player on square 1 (Old Kent Road)
    # and play the card again...
    player.state.square = 1
    card.play(game, player)

    # We check that going back wrapped around the board,
    # in this case to Super Tax...
    assert player.state.square == 38
    assert player.state.cash == 1200
