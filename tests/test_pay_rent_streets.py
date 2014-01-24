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


def test_with_houses():
    '''
    Tests that rents is calculated correctly for a property
    with houses.
    '''
    # We set up the game and the players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # We give the owner Trafalgar Square with three houses...
    trafalgar_square = game.give_property_to_player(owner, Square.Name.TRAFALGAR_SQUARE)
    trafalgar_square.number_of_houses = 3

    # The player starts on Free Parking, and rolls a 4...
    player.state.square = 20
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # The player should be on Trafalgar Square, and have paid the rent...
    assert player.state.square == 24
    assert player.state.cash == 750
    assert owner.state.cash == 2250


def test_player_does_not_have_enough_money():
    '''
    Tests the as much money as possible is given to the owner
    if a player lands on their property, but the player does
    not have enough money to pay in full.
    '''
    # We set up the game and the players...
    game = Game()
    player = game.add_player(DefaultPlayerAI())
    owner = game.add_player(DefaultPlayerAI())

    # We give the owner Mayfair with a hotel...
    trafalgar_square = game.give_property_to_player(owner, Square.Name.MAYFAIR)
    trafalgar_square.number_of_houses = 5

    # The player starts on Liverpool Street Station, and rolls a 4...
    player.state.square = 35
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # The player should be removed from the board, and should be bankrupt.
    # The owner should have got all the player's money...
    assert player.state.square == -1
    assert player.state.cash == -1
    assert owner.state.cash == 3000


