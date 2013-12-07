from monopyly import *
from testing_utils import *

# TODO: What happens if two players bid the same amount?


class PlayerWhoBidsInAuctions(PlayerAIBase):
    '''
    A player who bids in auctions.
    '''
    def __init__(self, next_bid=0):
        self.next_bid = next_bid

    def property_offered_for_auction(self, game_state, player_state, property_name, face_value):
        return self.next_bid


def test_two_players_both_bid():
    '''
    A test with two players. One lands on a property but does not
    buy it. Both bid in the auction. We confirm it goes to the
    highest bidder at the lower price + £1.
    '''
    # We set up the game with two players...
    game = Game()
    player0 = game.add_player(PlayerWhoBidsInAuctions(next_bid=150))
    player1 = game.add_player(PlayerWhoBidsInAuctions(next_bid=175))

    # Player 0 is on Just Visiting and rolls a 9 to end up on Vine Street...
    player0.state.square = 10
    game.dice = MockDice([(4, 5)])
    game.play_one_turn(player0)

    # Player 0 should not have any properties or paid any money...
    assert len(player0.state.property_indexes) == 0
    assert player0.state.cash == 1500

    # Player 1 should have won the auction and paid £151...
    assert len(player1.state.property_indexes) == 1
    assert 19 in player1.state.property_indexes
    assert player1.state.cash == 1349


def test_three_players_only_one_bids():
    '''
    A property is auctioned to three players, but only one bids.

    They should get the property for £1.
    '''
    # We set up the game with three players...
    game = Game()
    player0 = game.add_player(PlayerWhoBidsInAuctions(next_bid=150))
    player1 = game.add_player(PlayerWhoBidsInAuctions(next_bid=0))
    player2 = game.add_player(PlayerWhoBidsInAuctions(next_bid=0))

    # Player 0 is on Just Visiting and rolls a 9 to end up on Vine Street...
    player0.state.square = 10
    game.dice = MockDice([(4, 5)])
    game.play_one_turn(player0)

    # Player 0 should have won the auction and paid £1...
    assert len(player0.state.property_indexes) == 1
    assert 19 in player0.state.property_indexes
    assert player0.state.cash == 1499

    # Player 1 should not have any properties or paid any money...
    assert len(player1.state.property_indexes) == 0
    assert player1.state.cash == 1500

    # Player 2 should not have any properties or paid any money...
    assert len(player2.state.property_indexes) == 0
    assert player2.state.cash == 1500


def test_three_bids_but_highest_cannot_afford_it():
    '''
    Three bids are put in for the auction, but the top bidder
    cannot afford to pay.

    The property should go to the second highest bidder.
    '''
        # We set up the game with three players...
    game = Game()
    player0 = game.add_player(PlayerWhoBidsInAuctions(next_bid=200))
    player1 = game.add_player(PlayerWhoBidsInAuctions(next_bid=400))
    player2 = game.add_player(PlayerWhoBidsInAuctions(next_bid=300))

    # Player 1 has the highest bid, and should win the auction.
    # But they have less than the £301 required to buy the property...
    player1.state.cash = 250

    # Player 0 is on Just Visiting and rolls a 9 to end up on Vine Street...
    player0.state.square = 10
    game.dice = MockDice([(4, 5)])
    game.play_one_turn(player0)

    # Player 0 should not have any properties or paid any money...
    assert len(player0.state.property_indexes) == 0
    assert player0.state.cash == 1500

    # Player 1 should not have any properties or paid any money...
    assert len(player1.state.property_indexes) == 0
    assert player1.state.cash == 250

    # Player 2 should have won the auction and paid £201...
    assert len(player2.state.property_indexes) == 1
    assert 19 in player2.state.property_indexes
    assert player2.state.cash == 1299

