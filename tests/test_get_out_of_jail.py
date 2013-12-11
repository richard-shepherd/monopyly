from monopyly import *
from testing_utils import *


class PlayerWhoGetsOutOfJail(DefaultPlayerAI):
    '''
    A player who performs the given action when in jail.
    '''
    def __init__(self, action):
        self.action = action

    def set_action(self, action):
        self.action = action

    def get_out_of_jail(self, player):
        return self.action


def test_has_to_pay_on_third_turn():
    '''
    The player fails to roll doubles for the three turns inside
    and must pay £50.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.STAY_IN_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player doesn't roll doubles in the next three turns...
    game.dice = MockDice([(2, 3), (1, 4), (6, 4)])

    # We play the first turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 1

    # We play the second turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 2

    # We play the third turn. The player should have been forced
    # to pay their way out...
    game.play_one_turn(player)
    assert player.state.square == 20
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450


def test_roll_doubles_on_third_turn():
    '''
    Tests that rolling doubles on the third turn in jail gets you
    out of jail without paying (and that you don't get a turn afterwards).
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.STAY_IN_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player rolls double on the third turn...
    game.dice = MockDice([(2, 3), (1, 4), (5, 5), (1, 2)])

    # We play the first turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 1

    # We play the second turn...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 2

    # We play the third turn. The player rolls doubles to get out...
    game.play_one_turn(player)
    assert player.state.square == 20
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1500


def test_buy_way_out():
    '''
    The player buys their way out on the first turn.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player buys their way out then rolls 8...
    game.dice = MockDice([(3, 5)])

    # The player should have paid £50 and be on Marlborough Street...
    game.play_one_turn(player)
    assert player.state.square == 18
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450


def test_get_out_of_jail_free():
    '''
    The player has two Get Out Of Jail Free cards and plays one of them.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player has two Get Out Of Jail Free cards...
    player.state.get_out_of_jail_free_cards.append(GetOutOfJailFree())
    player.state.get_out_of_jail_free_cards.append(GetOutOfJailFree())

    # The player plays the card then rolls 8...
    game.dice = MockDice([(3, 5)])

    # The player should have used a card and be on Marlborough Street...
    game.play_one_turn(player)
    assert player.state.square == 18
    assert player.state.is_in_jail is False
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1500
    assert player.state.number_of_get_out_of_jail_free_cards == 1


def test_get_out_of_jail_free_no_card():
    '''
    The player tries to play a Get Out Of Jail Free card, but
     doesn't actually have one.
    '''
    # We create a game with a player, who we put in jail...
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player tries to play the card then rolls 8...
    game.dice = MockDice([(3, 5)])

    # The player should still be in jail...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 1
    assert player.state.cash == 1500
    assert player.state.number_of_get_out_of_jail_free_cards == 0


def test_out_jail_and_straight_back_again():
    '''
    The player pays their way out, rolls a 7 and picks up a Community
    Chest Go To Jail card.
    '''
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.BUY_WAY_OUT_OF_JAIL))
    player.state.square = 10
    player.state.is_in_jail = True
    player.state.number_of_turns_in_jail = 0

    # The player pays their way out then rolls 7 to land on Community Chest...
    game.dice = MockDice([(3, 4)])

    # The top Community Chest card is Go To Jail...
    game.state.board.community_chest_deck = MockCardDeck(GoToJailCard())

    # The player should be back in jail after paying £50...
    game.play_one_turn(player)
    assert player.state.square == 10
    assert player.state.is_in_jail is True
    assert player.state.number_of_turns_in_jail == 0
    assert player.state.cash == 1450


def test_get_out_of_jail_free_card():
    '''
    Tests that you get a GOOJF card when you land on Chance or
    Community Chest and it is the top card.

    Also tests that it is removed from the deck, and replaced when
    it is played.
    '''
    game = Game()
    player = game.add_player(PlayerWhoGetsOutOfJail(PlayerAIBase.Action.PLAY_GET_OUT_OF_JAIL_FREE_CARD))

    # We set up the chance deck with three cards, GOOJF on top...
    mock_chance_deck = MockCardDeck()
    mock_chance_deck.set_next_cards([GetOutOfJailFree(mock_chance_deck), RewardCard(100), FineCard(50)])
    game.state.board.chance_deck = mock_chance_deck

    # The player starts on Marlborough street and rolls four to land on
    # Chance, where they pick up a GOOJF card...
    player.state.square = 18
    game.dice = MockDice([(1, 3)])
    game.play_one_turn(player)

    # We check that the player now has a GOOJF card, and that the
    # Chance deck has one fewer card...
    assert player.state.number_of_get_out_of_jail_free_cards == 1
    assert game.state.board.chance_deck.number_of_cards == 2

    # They now roll eight to land on Go To Jail, and in the turn after
    # that they play the card...
    game.dice = MockDice([(5, 3), (4, 6)])
    game.play_one_turn(player)

    # The player should be in jail and have not yet played the card...
    assert player.state.is_in_jail is True
    assert player.state.number_of_get_out_of_jail_free_cards == 1
    assert game.state.board.chance_deck.number_of_cards == 2

    game.play_one_turn(player)

    # The player should be on Free Parking, not have the card and the
    # card should be back in the deck...
    assert player.state.is_in_jail is False
    assert player.state.square == 20
    assert player.state.number_of_get_out_of_jail_free_cards == 0
    assert game.state.board.chance_deck.number_of_cards == 3




