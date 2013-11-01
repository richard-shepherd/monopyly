from monopyly import *
from testing_utils import *


def test_one_utility_owned():
    '''
    Tests that rent is correctly collected when one
    utility is owned.
    '''
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner has one utility...
    game.give_property_to_player(owner, Square.Name.ELECTRIC_COMPANY)

    # The player starts at Pentonville Road and rolls a 3 to
    # land on the Electric Company...
    player.state.square = 9
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should be at the Electric Company and
    # have paid four times the roll of the dice...
    assert player.state.square == 12
    assert player.state.cash == 1488


def test_two_utilities_owned():
    '''
    Tests that rent is correctly collected when two
    utilities are owned.
    '''
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner has both utilities...
    game.give_property_to_player(owner, Square.Name.ELECTRIC_COMPANY)
    game.give_property_to_player(owner, Square.Name.WATER_WORKS)

    # The player starts at Pentonville Road and rolls a 3 to
    # land on the Electric Company...
    player.state.square = 9
    game.dice = MockDice([(1, 2)])
    game.play_one_turn(player)

    # The player should be at the Electric Company and
    # have paid ten times the roll of the dice...
    assert player.state.square == 12
    assert player.state.cash == 1470

