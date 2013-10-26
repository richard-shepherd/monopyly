from monopyly import *
from testing_utils import *


def test_it_is_your_birthday():
    '''
    Tests the "It is your birthday..." card.

    Includes testing the "house rule" that players have to say "Happy Birthday!"
    to the player, or pay an extra fine.
    '''

    # A player AI that says "Happy Birthday!"...
    class PlayerWhoSaysHappyBirthday(PlayerAIBase):
        def players_birthday(self):
            return "Happy Birthday!"

    # A player AI that does not say "Happy Birthday!"...
    class PlayerWhoDoesNotSayHappyBirthday(PlayerAIBase):
        pass

    # We set up a game with three players: the player who picks up
    # the card, one that says Happy Birthday! and one that does not...
    game = Game()
    game.add_player(DefaultPlayerAI())
    game.add_player(PlayerWhoSaysHappyBirthday())
    game.add_player(PlayerWhoDoesNotSayHappyBirthday())

    current_player = game.state.players[0]
    player_who_says_happy_birthday = game.state.players[1]
    player_who_does_not_say_happy_birthday = game.state.players[2]

    # The current player takes the "It is your birthday" card...
    card = ItIsYourBirthday()
    card.play(game, current_player)

    # The current player should have received £110...
    assert current_player.state.cash == 1610
    assert player_who_says_happy_birthday.state.cash == 1490
    assert player_who_does_not_say_happy_birthday.state.cash == 1400



