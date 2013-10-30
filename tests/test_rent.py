from monopyly import *
from testing_utils import *


def test_base_rent():
    '''
    Tests that the base rent is taken when you land on a square owned
    by another player (who does not own the whole set).
    '''
    # We set up the game and the players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # We give the owner Coventry Street...
    game.give_property_to_player(owner, Square.Name.COVENTRY_STREET)

    # The player starts on Free Parking, and rolls a 7...
    player.state.square = 20
    game.dice = MockDice([(2, 5)])
    game.play_one_turn(player)

    # The player should be on Coventry Street, and have paid the rent...
    assert player.state.square == 27
    assert player.state.cash == 1478
    assert owner.state.cash == 1522


def test_whole_set():
    '''
    Tests that double the base rent is taken when you land on a square owned
    by another player who also owns the whole set.
    '''
    # We set up the game and the players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # We give the owner the whole green set...
    game.give_property_to_player(owner, Square.Name.REGENT_STREET)
    game.give_property_to_player(owner, Square.Name.OXFORD_STREET)
    game.give_property_to_player(owner, Square.Name.BOND_STREET)

    # The player starts on Fenchurch Street Station, and rolls a 9...
    player.state.square = 25
    game.dice = MockDice([(4, 5)])
    game.play_one_turn(player)

    # The player should be on Bond Street, and have paid the rent...
    assert player.state.square == 34
    assert player.state.cash == 1444
    assert owner.state.cash == 1556

# TODO: test with houses


# TODO: Test when player does not have enough money