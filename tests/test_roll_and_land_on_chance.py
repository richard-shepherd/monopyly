from monopyly import *
from testing_utils import *


def test_roll_and_land_on_chance():
    '''
    Sets up a game and adds a player. The Community Chest deck is set
    up to fine the player £80. The Chance deck is set up to reward the
    player £120.

    The dice are set to roll a (1, 1) to land on Community Chest, then
    (2, 3) to land on Chance.

    We check that the player's cash is altered as we expect.
    This also tests that doubles causes the player to roll again.
    '''

    # We set up the game and the player...
    game = Game()
    player = game.add_player(DefaultPlayerAI())

    # We mock the card decks...
    mock_community_chest = MockCardDeck()
    mock_community_chest.set_next_card(FineCard(80))
    game.state.board.community_chest_deck = mock_community_chest

    mock_chance = MockCardDeck()
    mock_chance.set_next_card(RewardCard(120))
    game.state.board.chance_deck = mock_chance

    # We mock the dice...
    game.dice = MockDice([(1, 1), (2, 3)])

    # We play the turn, and check the results...
    game.play_one_turn(player)
    assert player.state.cash == 1540

