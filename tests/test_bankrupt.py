from monopyly import *
from testing_utils import *


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

    # Player 1 also owns Strand, which is mortgaged...
    strand = game.give_property_to_player(player1, Square.Name.STRAND)
    strand.is_mortgaged = True

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
    assert bow_street.owner is None
    assert marlborough_street.owner is None
    assert vine_street.owner is None
    assert strand.owner is None
    assert strand.is_mortgaged is False

    # We play another round. Player 1 should be out and should not move
    game.dice = MockDice([(4, 6), (4, 6), (6, 4)])
    game.play_one_round()
    assert player0.state.square == 20
    assert player1.state.square == -1
    assert player2.state.square == 20


def test_goojf_cards_returned():
    '''
    Tests that get Out Of Jail Free cards are returned to the
    decks when a player goes bankrupt.
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())
    player2 = game.add_player(DefaultPlayerAI())

    # We set up Community Chest with two cards...
    mock_deck = MockCardDeck()
    mock_deck.set_next_cards([GetOutOfJailFree(mock_deck), FineCard(100)])
    game.state.board.community_chest_deck = mock_deck

    # Player 1 will land on Community Chest and get a GOOJF card.
    # The other players do not move...
    player1.state.square = 29
    game.dice = MockDice([(6, 4), (1, 3), (6, 4)])
    game.play_one_round()

    assert player1.state.number_of_get_out_of_jail_free_cards == 1
    assert mock_deck.number_of_cards == 1

    # Player 1 lands on Super Tax and goes bankrupt...
    player1.state.cash = 50
    game.dice = MockDice([(6, 4), (2, 3), (6, 4)])
    game.play_one_round()

    assert mock_deck.number_of_cards == 2
    assert player1 not in game.state.players
    assert player1 in game.state.bankrupt_players


def test_player_goes_bankrupt_in_other_players_turn():
    '''
    A player goes bankrupt because another player lands on
    'It is your birthday...'
    '''
    game = Game()
    player0 = game.add_player(DefaultPlayerAI())
    player1 = game.add_player(DefaultPlayerAI())
    player2 = game.add_player(DefaultPlayerAI())

    # The Chance deck has an It is Your Birthday card
    # at the top...
    board = game.state.board
    board.chance_deck = MockCardDeck(ItIsYourBirthday())

    # player1 does not have enough money to give player0
    # a birthday present...
    player1.state.cash = 5

    # player0 rolls 7 and lands on Chance.
    # player1 should then be out of the game, and player2 then rolls 10.
    game.dice = MockDice([(2, 5), (4, 6)])
    game.play_one_round()

    assert player0 in game.state.players
    assert player1 not in game.state.players
    assert player2 in game.state.players
    assert player1 in game.state.bankrupt_players
    assert player2.state.square == 10



