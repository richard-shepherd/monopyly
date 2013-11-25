from monopyly import *
from testing_utils import *

# TODO: max rounds, net worth (not just cash)

# TODO: maximum rounds, equal net worth

def test_maximum_rounds():
    '''
    Tests that the game is over when the maximum number of rounds
    has been played.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())

    # We put both players on Free Parking and ensure that all dice
    # are zeros. Player1 has more money, so after the maximum number
    # of rounds, they should win...
    player0.state.square = 20
    player1.state.square = 20
    player0.state.cash = 1000
    player1.state.cash = 1200

    # We play the game...
    game.dice = MockDice(roll_results=[(0, 0)], repeat=True)
    game.maximum_rounds = 20
    game.play_game()

    # We check the winner and the turns played...
    assert game.number_of_rounds_played == game.maximum_rounds
    assert game.winner == player1


def test_maximum_rounds_net_worth_properties():
    '''
    One player has more money at the end of the game, but the other
    has the higher net worth because of properties.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())

    # player0 has more money...
    player0.state.cash = 1000
    player1.state.cash = 980

    # But player1 has more valuable properties...
    game.give_property_to_player(player0, Square.Name.BOW_STREET)
    game.give_property_to_player(player0, Square.Name.VINE_STREET)
    game.give_property_to_player(player1, Square.Name.STRAND)
    game.give_property_to_player(player1, Square.Name.FLEET_STREET)
    game.give_property_to_player(player1, Square.Name.TRAFALGAR_SQUARE)

    # We put both players on Free Parking and ensure that all dice
    # are zeros. Player1 has more money, so after the maximum number
    # of rounds, they should win...
    player0.state.square = 20
    player1.state.square = 20

    # We play the game...
    game.dice = MockDice(roll_results=[(0, 0)], repeat=True)
    game.maximum_rounds = 20
    game.play_game()

    # We check the winner and the turns played...
    assert player0.net_worth == 1000 + 90 + 100  # 1190
    assert player1.net_worth == 980 + 110 + 110 + 120  # 1320
    assert game.number_of_rounds_played == game.maximum_rounds
    assert game.winner == player1


def test_maximum_rounds_net_worth_properties_and_houses():
    '''
    One player has more money at the end of the game, the other
    has the higher net worth because of properties, but the first
    player has higher value houses.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())

    # player0 has more money...
    player0.state.cash = 1000
    player1.state.cash = 980

    # player1 has more valuable properties...
    bow_street = game.give_property_to_player(player0, Square.Name.BOW_STREET)
    marlborough_street = game.give_property_to_player(player0, Square.Name.MARLBOROUGH_STREET)
    vine_street = game.give_property_to_player(player0, Square.Name.VINE_STREET)
    strand = game.give_property_to_player(player1, Square.Name.STRAND)
    fleet_street = game.give_property_to_player(player1, Square.Name.FLEET_STREET)
    trafaglar_square = game.give_property_to_player(player1, Square.Name.TRAFALGAR_SQUARE)

    # But player0 has more valuable houses...
    bow_street.number_of_houses = 1
    marlborough_street.number_of_houses = 1
    vine_street.number_of_houses = 1
    trafaglar_square.number_of_houses = 1

    # We put both players on Free Parking and ensure that all dice
    # are zeros. Player1 has more money, so after the maximum number
    # of rounds, they should win...
    player0.state.square = 20
    player1.state.square = 20

    # We play the game...
    game.dice = MockDice(roll_results=[(0, 0)], repeat=True)
    game.maximum_rounds = 20
    game.play_game()

    # We check the winner and the turns played...
    assert player0.net_worth == 1000 + 90 + 90 + 100 + 3 * 50  # 1430
    assert player1.net_worth == 980 + 110 + 110 + 120 + 75  # 1395
    assert game.number_of_rounds_played == game.maximum_rounds
    assert game.winner == player0



