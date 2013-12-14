from monopyly import *
from testing_utils import *


def test_same_player():
    '''
    Tests that the is_same_player method works as expected.
    It should match players on Player identity or if the AIs match.
    '''
    game = Game()
    ai1 = DefaultPlayerAI()
    ai2 = DefaultPlayerAI()
    p1 = game.add_player(ai1)
    p2 = game.add_player(ai2)

    assert p1.is_same_player(p1)
    assert not p1.is_same_player(p2)
    assert p1.is_same_player(ai1)
    assert not p1.is_same_player(ai2)