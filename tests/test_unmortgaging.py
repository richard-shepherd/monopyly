from monopyly import *
from testing_utils import *


class PlayerWhoUnmortgages(PlayerAIBase):
    '''
    A player who unmortgages properties.
    '''
    def __init__(self, properties_to_unmortgage):
        self.properties_to_unmortgage = properties_to_unmortgage

    def unmortgage_properties(self, game_state, player_state):
        return self.properties_to_unmortgage


def test_owned_properties_got_enough_money():
    '''
    Simple unmortgaging where we have the money and where
    we own all the properties.
    '''
    # We give the player a number of mortgaged properties...
    game = Game()
    player = game.add_player(PlayerWhoUnmortgages([Square.Name.BOW_STREET, Square.Name.VINE_STREET]))
    bow_street = game.give_property_to_player(player, Square.Name.BOW_STREET)
    vine_street = game.give_property_to_player(player, Square.Name.VINE_STREET)
    bow_street.is_mortgaged = True
    vine_street.is_mortgaged = True

    # The player starts on Go and rolls 10 to get to Just Visiting.
    # The move is not important, but the turn triggers the opportunity
    # for unmortgaging...
    player.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player)

    # The properties should be unmortgaged and the player should have paid
    # (£100 + £90) + 10% = £209
    assert bow_street.is_mortgaged is False
    assert vine_street.is_mortgaged is False
    assert player.state.cash == 1291
    assert type(player.state.cash) == int


def test_unowned_properties():
    '''
    The player tries to unmortgage a property they do not own.
    '''
    # The player will try to unmortgage two of the orange properties,
    # but they only own ne of them...
    game = Game()
    player = game.add_player(PlayerWhoUnmortgages([Square.Name.BOW_STREET, Square.Name.VINE_STREET]))
    bow_street = game.give_property_to_player(player, Square.Name.BOW_STREET)
    bow_street.is_mortgaged = True

    # The player starts on Go and rolls 10 to get to Just Visiting.
    # The move is not important, but the turn triggers the opportunity
    # for unmortgaging...
    player.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player)

    # The transaction should have been aborted...
    assert player.state.cash == 1500
    assert bow_street.is_mortgaged is True


def test_not_enough_money():
    '''
    Unmortgaging should be aborted if the player does not
    have enough money.
    '''
    # We give the player a number of mortgaged properties...
    game = Game()
    player = game.add_player(PlayerWhoUnmortgages([Square.Name.BOW_STREET, Square.Name.VINE_STREET]))
    bow_street = game.give_property_to_player(player, Square.Name.BOW_STREET)
    vine_street = game.give_property_to_player(player, Square.Name.VINE_STREET)
    bow_street.is_mortgaged = True
    vine_street.is_mortgaged = True

    # Unmortgaging will cost (£100 + £90) + 10% = £209, but the
    # player only has £200...
    player.state.cash = 200

    # The player starts on Go and rolls 10 to get to Just Visiting.
    # The move is not important, but the turn triggers the opportunity
    # for unmortgaging...
    player.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player)

    # The transaction should have been aborted...
    assert bow_street.is_mortgaged is True
    assert vine_street.is_mortgaged is True
    assert player.state.cash == 200


def test_not_a_property():
    '''
    Unmortgaging should ignore squares which are not properties.
    '''
    # We give the player a number of mortgaged properties...
    game = Game()
    player = game.add_player(
        PlayerWhoUnmortgages(
            [Square.Name.BOW_STREET, Square.Name.VINE_STREET, Square.Name.FREE_PARKING]))
    bow_street = game.give_property_to_player(player, Square.Name.BOW_STREET)
    vine_street = game.give_property_to_player(player, Square.Name.VINE_STREET)
    bow_street.is_mortgaged = True
    vine_street.is_mortgaged = True

    # The player starts on Go and rolls 10 to get to Just Visiting.
    # The move is not important, but the turn triggers the opportunity
    # for unmortgaging...
    player.state.square = 0
    game.dice = MockDice([(4, 6)])
    game.play_one_turn(player)

    # The transaction should have been aborted...
    assert bow_street.is_mortgaged is False
    assert vine_street.is_mortgaged is False
    assert player.state.cash == 1291

