from monopyly import *
from testing_utils import *


class PlayerWhoSellsHouses(DefaultPlayerAI):
    '''
    A player who sells houses.
    '''
    def __init__(self, houses_to_sell=None):
        if not houses_to_sell:
            houses_to_sell = []
        self.houses_to_sell = houses_to_sell

    def sell_houses(self, game_state, player_state):
        return self.houses_to_sell


def test_simple_selling():
    '''
    Tests selling two houses from each of the pink set, except Northumberland
    Avenue where we sell one.
    '''
    game = Game()
    board = game.state.board
    player = game.add_player(PlayerWhoSellsHouses([
        (board.get_square_by_name(Square.Name.PALL_MALL), 2),
        (board.get_square_by_name(Square.Name.WHITEHALL), 2),
        (board.get_square_by_name(Square.Name.NORTHUMBERLAND_AVENUE), 1)]))

    # We give the player the pink set with four houses on
    # each property...
    pall_mall = game.give_property_to_player(player, Square.Name.PALL_MALL)
    whitehall = game.give_property_to_player(player, Square.Name.WHITEHALL)
    northumberland_avenue = game.give_property_to_player(player, Square.Name.NORTHUMBERLAND_AVENUE)
    pall_mall.number_of_houses = 4
    whitehall.number_of_houses = 4
    northumberland_avenue.number_of_houses = 4

    # We need to trigger a fine, so we start the player at Go
    # and move them to Income Tax...
    player.state.square = 0
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # The player should have received 5 x £50 for the houses
    # and paid £200 tax, and the properties should have fewer
    # houses...
    assert pall_mall.number_of_houses == 2
    assert whitehall.number_of_houses == 2
    assert northumberland_avenue.number_of_houses == 3
    assert player.state.cash == 1550


def test_sell_negative_number_of_houses():
    '''
    Tests that you cannot sell a -ve number of houses as a sneaky way
    of buying houses cheaply.
    '''
    game = Game()
    board = game.state.board
    player = game.add_player(PlayerWhoSellsHouses([
        (board.get_square_by_name(Square.Name.PALL_MALL), -5),
        (board.get_square_by_name(Square.Name.WHITEHALL), -5),
        (board.get_square_by_name(Square.Name.NORTHUMBERLAND_AVENUE), -5)]))

    # We give the player the pink set...
    pall_mall = game.give_property_to_player(player, Square.Name.PALL_MALL)
    whitehall = game.give_property_to_player(player, Square.Name.WHITEHALL)
    northumberland_avenue = game.give_property_to_player(player, Square.Name.NORTHUMBERLAND_AVENUE)

    # We need to trigger a fine, so we start the player at Go
    # and move them to Income Tax...
    player.state.square = 0
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # No houses should have been 'sold'...
    assert pall_mall.number_of_houses == 0
    assert whitehall.number_of_houses == 0
    assert northumberland_avenue.number_of_houses == 0

    # Only the tax should have been paid...
    assert player.state.cash == 1300


def test_selling_unowned_houses():
    '''
    Players should not be able to sell houses they do not have.
    '''
    game = Game()
    board = game.state.board
    player = game.add_player(PlayerWhoSellsHouses([
        (board.get_square_by_name(Square.Name.PALL_MALL), 100),
        (board.get_square_by_name(Square.Name.WHITEHALL), 100),
        (board.get_square_by_name(Square.Name.NORTHUMBERLAND_AVENUE), 100)]))

    # We give the player the pink set with four houses on
    # each property...
    pall_mall = game.give_property_to_player(player, Square.Name.PALL_MALL)
    whitehall = game.give_property_to_player(player, Square.Name.WHITEHALL)
    northumberland_avenue = game.give_property_to_player(player, Square.Name.NORTHUMBERLAND_AVENUE)
    pall_mall.number_of_houses = 4
    whitehall.number_of_houses = 4
    northumberland_avenue.number_of_houses = 4

    # We need to trigger a fine, so we start the player at Go
    # and move them to Income Tax...
    player.state.square = 0
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # Only the tax should have been taken...
    assert player.state.cash == 1300

    # No sale should have been made...
    assert pall_mall.number_of_houses == 4
    assert whitehall.number_of_houses == 4
    assert northumberland_avenue.number_of_houses == 4


def test_selling_another_players_houses():
    '''
    Player tries to sell houses belonging to another player.
    '''
    game = Game()
    board = game.state.board
    owner = game.add_player(DefaultPlayerAI())
    player = game.add_player(PlayerWhoSellsHouses([
        (board.get_square_by_name(Square.Name.PALL_MALL), 2),
        (board.get_square_by_name(Square.Name.WHITEHALL), 2),
        (board.get_square_by_name(Square.Name.NORTHUMBERLAND_AVENUE), 2)]))

    # We give the owner the pink set with four houses on each property...
    pall_mall = game.give_property_to_player(owner, Square.Name.PALL_MALL)
    whitehall = game.give_property_to_player(owner, Square.Name.WHITEHALL)
    northumberland_avenue = game.give_property_to_player(owner, Square.Name.NORTHUMBERLAND_AVENUE)
    pall_mall.number_of_houses = 4
    whitehall.number_of_houses = 4
    northumberland_avenue.number_of_houses = 4

    # We need to trigger a fine, so we start the player at Go
    # and move them to Income Tax...
    player.state.square = 0
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # No houses should have been sold, and only the tax paid...
    assert pall_mall.number_of_houses == 4
    assert whitehall.number_of_houses == 4
    assert northumberland_avenue.number_of_houses == 4
    assert player.state.cash == 1300


def test_unbalanced_selling():
    '''
    Tests selling houses where the sale will result in houses
    on the set not being balanced.

    The whole transaction should be rolled back, even if includes
    selling on other sets in a balanced way.
    '''
    # The player will sell two houses on Pall Mall and Whitehall, but try to leave
    # four houses on Northumberland Ave...
    game = Game()
    board = game.state.board
    player = game.add_player(PlayerWhoSellsHouses([
        (board.get_square_by_name(Square.Name.PALL_MALL), 2),
        (board.get_square_by_name(Square.Name.WHITEHALL), 2),
        (board.get_square_by_name(Square.Name.OLD_KENT_ROAD), 1),
        (board.get_square_by_name(Square.Name.WHITECHAPEL_ROAD), 1)]))

    # We give the player the pink set with four houses on each property,
    # and the brown set with three houses on each...
    pall_mall = game.give_property_to_player(player, Square.Name.PALL_MALL)
    whitehall = game.give_property_to_player(player, Square.Name.WHITEHALL)
    northumberland_avenue = game.give_property_to_player(player, Square.Name.NORTHUMBERLAND_AVENUE)
    old_ken_road = game.give_property_to_player(player, Square.Name.OLD_KENT_ROAD)
    whitechapel_road = game.give_property_to_player(player, Square.Name.WHITECHAPEL_ROAD)
    pall_mall.number_of_houses = 4
    whitehall.number_of_houses = 4
    northumberland_avenue.number_of_houses = 4
    old_ken_road.number_of_houses = 3
    whitechapel_road.number_of_houses = 3

    # We need to trigger a fine, so we start the player at Go
    # and move them to Income Tax...
    player.state.square = 0
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # No selling should have occurred, and only the tax taken...
    assert pall_mall.number_of_houses == 4
    assert whitehall.number_of_houses == 4
    assert northumberland_avenue.number_of_houses == 4
    assert old_ken_road.number_of_houses == 3
    assert whitechapel_road.number_of_houses == 3
    assert player.state.cash == 1300



