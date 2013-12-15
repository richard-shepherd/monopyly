from monopyly import *
from monopyly.game import deal_response
from testing_utils import *


class DealProposer(PlayerAIBase):
    '''
    A player who proposes deals.
    '''
    def __init__(self, deal_proposal):
        self.deal_proposals = [deal_proposal, None, None]
        self.index = 0
        self.deal_info = -1

    def propose_deal(self, game_state, player_state):
        if self.index >= len(self.deal_proposals):
            return None
        else:
            proposal = self.deal_proposals[self.index]
            self.index += 1
            return proposal

    def deal_result(self, deal_info):
        self.deal_info = deal_info


class DealResponder(PlayerAIBase):
    '''
    A player who responds to a deal.
    '''
    def __init__(self, deal_response):
        self.deal_response = deal_response
        self.deal_info = -1

    def deal_proposed(self, game_state, player, deal_proposal):
        return self.deal_response

    def deal_result(self, deal_info):
        self.deal_info = deal_info


def test_buy_mayfair():
    '''
    player0 proposes to buy Mayfair from player1, who accepts.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=500)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            maximum_cash_offered=1000)))

    # We give Mayfair to player1...
    mayfair = game.give_property_to_player(player1, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should now belong to player0 who should have
    # paid £750 for it...
    assert mayfair.owner is player0
    assert player0.state.cash == 750
    assert player1.state.cash == 2250

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED


def test_sell_mayfair():
    '''
    player0 proposes to sell Mayfair to player1, who accepts.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            maximum_cash_offered=1200)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_offered=[board.get_square_by_name(Square.Name.MAYFAIR)],
            minimum_cash_wanted=1000)))

    # We give Mayfair to player0...
    mayfair = game.give_property_to_player(player0, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should now belong to player1 who should have
    # paid £1100 for it...
    assert mayfair.owner is player1
    assert player0.state.cash == 2600
    assert player1.state.cash == 400

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED


def test_buy_mayfair_but_player_does_not_own_it():
    '''
    player0 proposes to buy Mayfair from player1, who accepts but does not own it.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=500)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            maximum_cash_offered=1000)))

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should not belong to anyone, no money should have changed hands...
    mayfair = game.state.board.get_square_by_name(Square.Name.MAYFAIR)
    assert mayfair.owner is None
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED


def test_sell_mayfair_but_player_does_not_own_it():
    '''
    player0 proposes to sell Mayfair to player1, who accepts. But player0 doesn't own it.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            maximum_cash_offered=1200)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_offered=[board.get_square_by_name(Square.Name.MAYFAIR)],
            minimum_cash_wanted=1000)))

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should not be owned and no money should have
    # changed hands...
    mayfair = game.state.board.get_square_by_name(Square.Name.MAYFAIR)
    assert mayfair.owner is None
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED


def test_buy_mayfair_player_doesnt_have_enough_money():
    '''
    player0 proposes to buy Mayfair from player1, who accepts. But player0
    does not have enough money for the deal value.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=600)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            maximum_cash_offered=1000)))

    # We give Mayfair to player1...
    mayfair = game.give_property_to_player(player1, Square.Name.MAYFAIR)

    # Player 0 has £700 which is not enough for the deal which
    # gets agreed at £800
    player0.state.cash = 700

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should still belong to player 1 and no
    # money should have changed hands...
    assert mayfair.owner is player1
    assert player0.state.cash == 700
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY


def test_sell_mayfair_player_doesnt_have_enough_money():
    '''
    player0 proposes to sell Mayfair to player1, who accepts. But player1
    does not have enough money for the deal value.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            maximum_cash_offered=1600)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_offered=[board.get_square_by_name(Square.Name.MAYFAIR)],
            minimum_cash_wanted=1000)))

    # We give Mayfair to player0...
    mayfair = game.give_property_to_player(player0, Square.Name.MAYFAIR)

    # Player1 has £1200 which is not enough for the deal which
    # gets agreed at £1300
    player1.state.cash = 1200

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should still belong to player 0 and no
    # money should have changed hands...
    assert mayfair.owner is player0
    assert player0.state.cash == 1500
    assert player1.state.cash == 1200

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.PLAYER_DID_NOT_HAVE_ENOUGH_MONEY


def test_invalid_player():
    '''
    player0 proposes to buy Mayfair from None, who does not exist.
    '''
    game = Game()
    board = game.state.board
    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=None,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            maximum_cash_offered=1000)))

    # Player 0 takes a turn during which the deal is attempted to be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # No deal should have been made...
    mayfair = game.state.board.get_square_by_name(Square.Name.MAYFAIR)
    assert mayfair.owner is None
    assert player0.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED


def test_buy_free_parking():
    '''
    player0 proposes to buy Free Parking from player1, who accepts.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=500)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.FREE_PARKING)],
            maximum_cash_offered=1000)))

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # The deal should have been rejected...
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED


def test_exchange_properties_plus_cash():
    '''
    An exchange of properties, with some cash to sweeten the deal.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=200)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            properties_offered=[board.get_square_by_name(Square.Name.VINE_STREET)],
            maximum_cash_offered=400)))

    # We give Vine Street to player0 and Mayfair to player1...
    vine_street = game.give_property_to_player(player0, Square.Name.VINE_STREET)
    mayfair = game.give_property_to_player(player1, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # The properties should be owned by the other players, and
    # £300 should have changed hands...
    assert mayfair.owner is player0
    assert vine_street.owner is player1
    assert player0.state.cash == 1200
    assert player1.state.cash == 1800

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED


def test_exchange_properties_no_cash():
    '''
    An exchange of properties, with no additional cash.
    '''
    game = Game()
    board = game.state.board
    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=0)))

    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player=player1,
            properties_wanted=[board.get_square_by_name(Square.Name.MAYFAIR)],
            properties_offered=[board.get_square_by_name(Square.Name.VINE_STREET)],
            maximum_cash_offered=0)))

    # We give Vine Street to player0 and Mayfair to player1...
    vine_street = game.give_property_to_player(player0, Square.Name.VINE_STREET)
    mayfair = game.give_property_to_player(player1, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # The properties should be owned by the other players, and
    # £300 should have changed hands...
    assert mayfair.owner is player0
    assert vine_street.owner is player1
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.SUCCEEDED

