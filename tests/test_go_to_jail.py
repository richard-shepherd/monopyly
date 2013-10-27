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
