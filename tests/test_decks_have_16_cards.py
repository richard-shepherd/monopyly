from monopyly import *


def test_decks_have_16_cards():
    '''
    Tests that the Chance and Community Chest decks each
    have 16 cards.
    '''
    game = Game()
    assert len(game.state.board.chance_deck.cards) == 16
    assert len(game.state.board.community_chest_deck.cards) == 16

