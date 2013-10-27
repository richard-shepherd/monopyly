from monopyly import *
from testing_utils import *


def test_go_to_jail_card_1():
    '''
    Tests that the "Go to jail" card sends the player to jail.
    '''
    # We set up the game...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # We play the card...
    card = GoToJailCard()
    card.play(game, player)

    # The player should be in jail...
    assert player.state.square == 10
    assert player.state.in_jail == True
    assert player.state.number_of_turns_in_jail == 0


def test_go_to_jail_square_1():
    '''
    Tests that landing on the Go To Jail square sends you to jail.
    '''
    # We set up the game...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # And mock the dice...
    mock_dice = MockDice()
    game.dice = mock_dice
    mock_dice.set_roll_results([(2, 4)])

    # The player starts on square 24 (Trafalgar Square) and we
    # roll a six (not as doubles) to end up on Go To Jail...
    player.state.square = 24
    game.play_one_turn(player)

    # The player should be in jail...
    assert player.state.square == 10
    assert player.state.in_jail is True
    assert player.state.number_of_turns_in_jail == 0


def test_go_to_jail_square_2():
    '''
    Tests that the players go ends when sent to jail, even if they
    rolled doubles. This is the same test as above, but with doubles
    rolled.
    '''
    # We set up the game...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # And mock the dice...
    mock_dice = MockDice()
    game.dice = mock_dice
    mock_dice.set_roll_results([(3, 3), [3, 4]])

    # The player starts on square 24 (Trafalgar Square) and we
    # roll a six (not as doubles) to end up on Go To Jail...
    player.state.square = 24
    game.play_one_turn(player)

    # The player should be in jail...
    assert player.state.square == 10
    assert player.state.in_jail is True
    assert player.state.number_of_turns_in_jail == 0


def test_roll_doubles_three_times():
    '''
    Tests that you get sent to jail for rolling doubles three times.
    '''
    # We set up the game...
    game = Game()
    game.add_player(DefaultPlayerAI())
    player = game.state.players[0]

    # And mock the dice. In this case, we roll double-zero
    # three times (as it makes other interactions simpler
    # if the player doesn't move).
    mock_dice = MockDice()
    game.dice = mock_dice
    mock_dice.set_roll_results([(0, 0), (0, 0), (0, 0), [3, 4]])

    # The player starts on square 20 (Free Parking) and
    # rolls (0, 0) three times (not moving), but should
    # end up in jail...
    player.state.square = 20
    game.play_one_turn(player)

    # The player should be in jail...
    assert player.state.square == 10
    assert player.state.in_jail is True
    assert player.state.number_of_turns_in_jail == 0
