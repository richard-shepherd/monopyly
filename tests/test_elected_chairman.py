from monopyly import Game
from monopyly import ElectedChairman
from testing_utils import DefaultPlayerAI


def test_elected_chairman():
    '''
    Tests the "You have been elected chairman or the board"
    Chance card.
    '''
    # We set up a game with 4 players...
    game = Game()
    player1 = game.add_player(DefaultPlayerAI())
    player2 = game.add_player(DefaultPlayerAI())
    player3 = game.add_player(DefaultPlayerAI())
    player4 = game.add_player(DefaultPlayerAI())

    # Player 2 picks up the 'elected chairman' card...
    card = ElectedChairman()
    card.play(game, player2)

    # We check that player2 has paid £50 to each of the
    # other players...
    assert player1.state.cash == 1550
    assert player2.state.cash == 1350
    assert player3.state.cash == 1550
    assert player4.state.cash == 1550
