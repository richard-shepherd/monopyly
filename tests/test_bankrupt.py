from monopyly import *
from testing_utils import *

# TODO: test return of GOOJF cards

def test_player_goes_bankrupt():
    '''
    A player goes bankrupt by landing on Mayfair with 4 houses.

    We check that the player is marked as bankrupt and that all
    their properties are returned to the bank.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())
    player2 = game.add_player(DefaultPlayerAI())

    # Player 0 owns Mayfair & Park Lane with 4 houses...
    park_lane = game.give_property_to_player(player0, Square.Name.PARK_LANE)
    mayfair = game.give_property_to_player(player0, Square.Name.MAYFAIR)
    park_lane.number_of_houses = 4
    mayfair.number_of_houses = 4

    # Players 0 and 2 will move from Go to Just Visiting, player 1
    # starts on Liverpool Street and rolls 4 to land on Mayfair...
    player0.state.square = 0
    player1.state.square = 35
    player2.state.square = 0

    # Player 1 has the orange set (which he does not even try to mortgage)
    # with 2 houses on each...
    bow_street = game.give_property_to_player(player1, Square.Name.BOW_STREET)
    marlborough_street = game.give_property_to_player(player1, Square.Name.MARLBOROUGH_STREET)
    vine_street = game.give_property_to_player(player1, Square.Name.VINE_STREET)
    bow_street.number_of_houses = 2
    marlborough_street.number_of_houses = 2
    vine_street.number_of_houses = 2

    # Player 1 does not have enough money to pay the rent (which is £1700)
    player1.state.cash = 500

    # We play a round of the game...
    game.dice = MockDice([(4, 6), (3, 1), (6, 4)])
    game.play_one_round()

    # Player 0 should have gained all player1's cash.
    # Player 1 should be bankrupt, and all houses and properties
    # returned to the bank...
    assert player0.state.cash == 2000
    assert player1 in game.state.bankrupt_players
    assert player1 not in game.state.players
    assert bow_street.number_of_houses == 0
    assert marlborough_street.number_of_houses == 0
    assert vine_street.number_of_houses == 0
    assert bow_street.owner_player_number == Property.NOT_OWNED
    assert marlborough_street.owner_player_number == Property.NOT_OWNED
    assert vine_street.owner_player_number == Property.NOT_OWNED

    # We play another round. Player 1 should be out and should not move
    game.dice = MockDice([(4, 6), (4, 6), (6, 4)])
    game.play_one_round()
    assert player0.state.square == 20
    assert player1.state.square == 39
    assert player2.state.square == 20






