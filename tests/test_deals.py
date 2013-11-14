from monopyly import *
from monopyly.game import deal_response
from testing_utils import *

# TODO: propose to an invalid player number

# TODO: paying player does not have enough money (test with both players)

# TODO: deal including a non-property


class DealProposer(PlayerAIBase):
    '''
    A player who proposes deals.
    '''
    def __init__(self, deal_proposal):
        self.deal_proposals = [deal_proposal, DealProposal(), DealProposal()]
        self.index = 0
        self.deal_info = -1

    def propose_deal(self, game_state, player_state):
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

    def deal_proposed(self, game_state, player_state, deal_proposal):
        return self.deal_response

    def deal_result(self, deal_info):
        self.deal_info = deal_info


def test_buy_mayfair():
    '''
    player0 proposes to buy Mayfair from player1, who accepts.
    '''
    game = Game()
    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player_number=1,
            properties_wanted=[Square.Name.MAYFAIR],
            maximum_cash_offered=1000)))

    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=500)))

    # We give Mayfair to player1...
    mayfair = game.give_property_to_player(player1, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should now belong to player0 who should have
    # paid £750 for it...
    assert mayfair.owner_player_number == 0
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
    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player_number=1,
            properties_offered=[Square.Name.MAYFAIR],
            minimum_cash_wanted=1000)))

    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            maximum_cash_offered=1200)))

    # We give Mayfair to player0...
    mayfair = game.give_property_to_player(player0, Square.Name.MAYFAIR)

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should now belong to player1 who should have
    # paid £1100 for it...
    assert mayfair.owner_player_number == 1
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
    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player_number=1,
            properties_wanted=[Square.Name.MAYFAIR],
            maximum_cash_offered=1000)))

    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            minimum_cash_wanted=500)))

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should not belong to anyone, no money should have changed hands...
    mayfair = game.state.board.get_square_by_name(Square.Name.MAYFAIR)
    assert mayfair.owner_player_number == Property.NOT_OWNED
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED


def test_sell_mayfair_but_player_does_not_own_it():
    '''
    player0 proposes to sell Mayfair to player1, who accepts. But player0 doesn't own it.
    '''
    game = Game()
    player0 = game.add_player(DealProposer(
        DealProposal(
            propose_to_player_number=1,
            properties_offered=[Square.Name.MAYFAIR],
            minimum_cash_wanted=1000)))

    player1 = game.add_player(DealResponder(
        DealResponse(
            DealResponse.Action.ACCEPT,
            maximum_cash_offered=1200)))

    # Player 0 takes a turn during which the deal should be done...
    player0.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player0)

    # Mayfair should not be owned and no money should have
    # changed hands...
    mayfair = game.state.board.get_square_by_name(Square.Name.MAYFAIR)
    assert mayfair.owner_player_number == Property.NOT_OWNED
    assert player0.state.cash == 1500
    assert player1.state.cash == 1500

    # We check that the players were notified correctly...
    assert player0.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED
    assert player1.ai.deal_info == PlayerAIBase.DealInfo.INVALID_DEAL_PROPOSED

