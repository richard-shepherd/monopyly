from monopyly import *
from monopyly.game import deal_response
from testing_utils import *

# TODO: propose to an invalid player number

# TODO: make sure the deal_result callback is called

# TODO: paying player does not have enough money (test with both players)

# TODO: players do not have the properties proposed


class DealProposer(PlayerAIBase):
    '''
    A player who proposes deals.
    '''
    def __init__(self, deal_proposal):
        self.deal_proposals = [deal_proposal, DealProposal(), DealProposal()]
        self.index = 0

    def propose_deal(self, game_state, player_state):
        proposal = self.deal_proposals[self.index]
        self.index += 1
        return proposal

class DealResponder(PlayerAIBase):
    '''
    A player who responds to a deal.
    '''
    def __init__(self, deal_response):
        self.deal_response = deal_response

    def deal_proposed(self, game_state, player_state, deal_proposal):
        return self.deal_response


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
