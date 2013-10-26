from monopyly import *
from testing_utils import *


def test_go_back():
    '''
    Tests the "Go back..." cards. These move the player, but without
    passing Go.
    '''
    # We set up a game with one player...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # We put the player on square 16 (Bow Street) and send them
    # 'back' to Free Parking...
    player.state.square = 16
    go_back_to_free_parking = GoBack(Square.Name.FREE_PARKING)
    go_back_to_free_parking.play(game, player)

    # The player should be at Free Parking (square 20) and should
    # not have any extra money for passing Go...
    assert player.state.square == 20
    assert player.state.cash == 1500

    # This time we start the player at square 23 (Fleet Street) and
    # go back to Free Parking again. The player should still not have
    # passed Go...
    player.state.square = 23
    go_back_to_free_parking.play(game, player)
    assert player.state.square == 20
    assert player.state.cash == 1500
