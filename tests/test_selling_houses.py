from monopyly import *
from testing_utils import *


class PlayerWhoSellsHouses(DefaultPlayerAI):
    '''
    A player who sells houses.
    '''
    def __init__(self, houses_to_sell=None):
        if(not houses_to_sell):
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
    player = game.add_player(PlayerWhoSellsHouses(
        [(Square.Name.PALL_MALL, 2),
         (Square.Name.WHITEHALL, 2),
         (Square.Name.NORTHUMBERLAND_AVENUE, 1)]))

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
    assert pall_mall.number_of_houses == 3
    assert player.state.cash == 1550

