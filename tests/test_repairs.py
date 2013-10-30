from monopyly import *
from testing_utils import *


def test_street_repairs():
    '''
    Tests the 'You are assessed for street repairs...' cards.
    '''
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    # The player has 4 houses on each of the purple set...
    street = game.give_property_to_player(player, Street.Name.PALL_MALL)
    street.number_of_houses = 4
    street = game.give_property_to_player(player, Street.Name.WHITEHALL)
    street.number_of_houses = 4
    street = game.give_property_to_player(player, Street.Name.NORTHUMBERLAND_AVENUE)
    street.number_of_houses = 4

    # And hotels on the brown set...
    street = game.give_property_to_player(player, Street.Name.OLD_KENT_ROAD)
    street.number_of_houses = 5
    street = game.give_property_to_player(player, Street.Name.WHITECHAPEL_ROAD)
    street.number_of_houses = 5

    # We player the 'Street repairs' card on the player...
    card = Repairs(amount_per_house=50, amount_per_hotel=125)
    card.play(game, player)

    # The player should have paid 12 * 50 + 2 * 125, ie 850...
    assert player.state.cash == 650






