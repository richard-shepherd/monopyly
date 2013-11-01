from monopyly import *
from testing_utils import *


def test_one_station():
    '''
    Tests that rent of £25 is taken when the owner owns one station.
    '''
    # We set up a game with two players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner owns one station...
    game.give_property_to_player(owner, Square.Name.LIVERPOOL_STREET_STATION)

    # The player starts on Piccadilly and rolls a 6 to land
    # on the station...
    player.state.square = 29
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)

    # The player should be on the station and have paid £25 rent...
    assert player.state.square == 35
    assert player.state.cash == 1475


def test_two_stations():
    '''
    Tests that rent of £50 is taken when the owner owns two stations.
    '''
    # We set up a game with two players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner owns two stations...
    game.give_property_to_player(owner, Square.Name.LIVERPOOL_STREET_STATION)
    game.give_property_to_player(owner, Square.Name.MARYLEBONE_STATION)

    # The player starts on Piccadilly and rolls a 6 to land
    # on the station...
    player.state.square = 29
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)

    # The player should be on the station and have paid £50 rent...
    assert player.state.square == 35
    assert player.state.cash == 1450


def test_three_stations():
    '''
    Tests that rent of £100 is taken when the owner owns three stations.
    '''
    # We set up a game with two players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner owns three stations...
    game.give_property_to_player(owner, Square.Name.LIVERPOOL_STREET_STATION)
    game.give_property_to_player(owner, Square.Name.MARYLEBONE_STATION)
    game.give_property_to_player(owner, Square.Name.KINGS_CROSS_STATION)

    # The player starts on Piccadilly and rolls a 6 to land
    # on the station...
    player.state.square = 29
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)

    # The player should be on the station and have paid £100 rent...
    assert player.state.square == 35
    assert player.state.cash == 1400


def test_four_stations():
    '''
    Tests that rent of £200 is taken when the owner owns four stations.
    '''
    # We set up a game with two players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # The owner owns four stations...
    game.give_property_to_player(owner, Square.Name.LIVERPOOL_STREET_STATION)
    game.give_property_to_player(owner, Square.Name.MARYLEBONE_STATION)
    game.give_property_to_player(owner, Square.Name.KINGS_CROSS_STATION)
    game.give_property_to_player(owner, Square.Name.FENCHURCH_STREET_STATION)

    # The player starts on Piccadilly and rolls a 6 to land
    # on the station...
    player.state.square = 29
    game.dice = MockDice([(2, 4)])
    game.play_one_turn(player)

    # The player should be on the station and have paid £200 rent...
    assert player.state.square == 35
    assert player.state.cash == 1300


